from __future__ import annotations

import os
from typing import Dict, List, Optional

from src.core.contracts import (
    Chunk,
    Chunker,
    EmbeddingProvider,
    PMOAnswer,
    Reranker,
    VectorStore,
)
from src.core.exceptions import AIQueryError, IngestionError
from src.observability.metrics import METRICS
from src.observability.tracing import timer


class PMOPipeline:
    """
    Orchestrates methodology document indexing and AI-powered PMO Q&A.

    Two responsibilities:
      1. Index PM methodology docs into a vector store for semantic retrieval
      2. Answer natural-language PMO questions by combining retrieved
         methodology passages with live PMO analysis context

    Separate from the PMO analysis engine (src/pmo/, src/risk/, src/okr/).
    This pipeline handles the RAG/AI layer only.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        chunker: Chunker,
        reranker: Optional[Reranker] = None,
        openai_api_key: Optional[str] = None,
    ) -> None:
        self._embedding = embedding_provider
        self._store = vector_store
        self._chunker = chunker
        self._reranker = reranker
        self._openai_key = openai_api_key
        self._indexed = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def index_methodology_docs(self, docs_dir: str) -> Dict:
        """
        Index all .md and .txt files in docs_dir into the vector store.
        Returns a summary dict with counts and file list.
        """
        from src.ingestion.document_loader import DocumentLoader
        from src.ingestion.text_cleaner import TextCleaner

        loader = DocumentLoader()
        cleaner = TextCleaner()

        if not os.path.isdir(docs_dir):
            raise IngestionError(f"Methodology docs directory not found: {docs_dir}")

        doc_files = [
            os.path.join(docs_dir, f)
            for f in os.listdir(docs_dir)
            if f.endswith((".md", ".txt"))
        ]

        total_chunks = 0
        indexed_files = []

        for path in doc_files:
            try:
                doc = loader.load_document(path)
                doc.text = cleaner.clean_text(doc.text)
                chunks = self._chunker.chunk(doc)

                with timer() as t:
                    for chunk in chunks:
                        [embedding] = self._embedding.embed([chunk.text])
                        chunk.embedding = embedding

                METRICS.embedding_latency_seconds += t["elapsed"]

                self._store.add(chunks)
                self._store.persist()
                total_chunks += len(chunks)
                indexed_files.append(os.path.basename(path))
                METRICS.documents_loaded_total += 1
                METRICS.chunks_created_total += len(chunks)
            except Exception as exc:
                METRICS.record_error(str(exc))

        self._indexed = True
        return {
            "docs_indexed": len(indexed_files),
            "total_chunks": total_chunks,
            "files": indexed_files,
        }

    def query(self, question: str, pmo_context: Dict, top_k: int = 5) -> PMOAnswer:
        """
        Answer a PMO question.

        Flow:
          1. Embed the question
          2. Retrieve relevant methodology passages (if index is ready)
          3. Generate answer via OpenAI (if key available) or rule-based mock
        """
        if not question or not question.strip():
            raise AIQueryError("Question cannot be empty.")

        METRICS.query_count_total += 1
        sources: List[str] = []
        methodology_context = ""

        # Retrieve methodology passages if index is ready
        if self._indexed:
            try:
                with timer() as t:
                    [q_embedding] = self._embedding.embed([question])
                    chunks = self._store.search(q_embedding, top_k)
                METRICS.retrieval_latency_seconds += t["elapsed"]

                if self._reranker:
                    chunks = self._reranker.rerank(question, chunks)

                sources = list({
                    c.metadata.get("file_name", c.doc_id)
                    for c in chunks if c.text
                })
                methodology_context = "\n\n---\n\n".join(
                    c.text for c in chunks[:3] if c.text
                )
            except Exception as exc:
                METRICS.record_error(str(exc))

        # Generate answer
        try:
            if self._openai_key and self._openai_key.strip():
                answer, mode = self._openai_answer(question, pmo_context, methodology_context)
            else:
                answer, mode = self._mock_answer(question, pmo_context), "mock"
        except Exception as exc:
            METRICS.record_error(str(exc))
            answer = "Unable to generate answer. Please try again."
            mode = "error"

        data_points = _extract_data_points(pmo_context)

        return PMOAnswer(
            question=question,
            answer=answer,
            sources=sources,
            data_points=data_points,
            mode=mode,
        )

    @property
    def is_indexed(self) -> bool:
        return self._indexed

    # ------------------------------------------------------------------
    # Answer generation — OpenAI path
    # ------------------------------------------------------------------

    def _openai_answer(self, question: str, ctx: Dict,
                       methodology: str) -> tuple[str, str]:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AIQueryError("openai package not installed.") from exc

        client = OpenAI(api_key=self._openai_key)

        system_prompt = (
            "You are an experienced PMO analyst assistant. "
            "Answer the project manager's question using the project data and "
            "methodology context provided. Be concise, practical, and action-oriented. "
            "Use bullet points for multi-part answers. Prioritize what the PM needs to act on."
        )

        project_summary = _format_context_for_prompt(ctx)
        user_prompt = (
            f"Project context:\n{project_summary}\n\n"
            f"Methodology reference:\n{methodology or 'N/A'}\n\n"
            f"Question: {question}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip(), "openai"

    # ------------------------------------------------------------------
    # Answer generation — Mock / rule-based path (no API key needed)
    # ------------------------------------------------------------------

    def _mock_answer(self, question: str, ctx: Dict) -> str:
        q = question.lower()

        if any(w in q for w in ["status", "health", "overview", "how is", "summary"]):
            return _answer_health(ctx)
        if any(w in q for w in ["blocker", "blocked", "stuck", "impediment"]):
            return _answer_blockers(ctx)
        if any(w in q for w in ["sprint", "velocity", "progress", "sprint 7"]):
            return _answer_sprint(ctx)
        if any(w in q for w in ["risk", "at risk", "danger", "concern"]):
            return _answer_risks(ctx)
        if any(w in q for w in ["okr", "objective", "goal", "key result"]):
            return _answer_okrs(ctx)
        if any(w in q for w in ["focus", "priority", "this week", "next step", "recommend"]):
            return _answer_focus(ctx)
        if any(w in q for w in ["retro", "retrospective", "improve", "learn"]):
            return _answer_retro(ctx)
        if any(w in q for w in ["capacity", "workload", "overload", "who is busy"]):
            return _answer_capacity(ctx)
        if any(w in q for w in ["overdue", "late", "deadline", "missed"]):
            return _answer_overdue(ctx)

        return _answer_general(ctx)


# ------------------------------------------------------------------
# Mock response generators
# ------------------------------------------------------------------

def _answer_health(ctx: Dict) -> str:
    score = ctx.get("health_score", "Unknown")
    summary = ctx.get("health_summary", "")
    sprint_pct = ctx.get("sprint_progress_pct", 0)
    done = ctx.get("done", 0)
    total = ctx.get("total_tasks", 0)
    stuck = ctx.get("stuck", 0)
    blocked = ctx.get("blocked", 0)
    return (
        f"**Project Health: {score}**\n\n"
        f"{summary}\n\n"
        f"- Tasks: {done}/{total} done ({sprint_pct:.0f}% sprint progress)\n"
        f"- {stuck} stuck, {blocked} blocked\n"
        f"- {ctx.get('overdue_count', 0)} overdue task(s)\n"
        f"- {ctx.get('risk_count', 0)} open risk(s)\n\n"
        f"*Note: This is a demo response. Connect an OpenAI key for AI-generated insights.*"
    )


def _answer_blockers(ctx: Dict) -> str:
    blockers = ctx.get("open_blockers", [])
    stuck = ctx.get("stuck", 0)
    blocked = ctx.get("blocked", 0)
    if not blockers:
        return "No active blockers detected in the current dataset."
    lines = [f"**{stuck + blocked} task(s) are stuck or blocked:**\n"]
    for b in blockers[:5]:
        lines.append(f"- **{b['name']}** (owner: {b['owner']})\n  ↳ {b['blocker']}")
    lines.append(
        f"\n**Recommended action:** Escalate the oldest blockers in today's standup. "
        "Scrum Master should own resolution within 24 hours."
    )
    return "\n".join(lines)


def _answer_sprint(ctx: Dict) -> str:
    sprint = ctx.get("active_sprint", "N/A")
    goal = ctx.get("sprint_goal", "")
    velocity = ctx.get("sprint_velocity", 0)
    health = ctx.get("sprint_health", "Unknown")
    planned = ctx.get("sprint_planned_pts", 0)
    completed = ctx.get("sprint_completed_pts", 0)
    load = ctx.get("team_load", {})
    return (
        f"**{sprint} — {health}**\n\n"
        f"Goal: {goal}\n\n"
        f"- Progress: {completed}/{planned} points ({velocity:.0%} velocity)\n"
        f"- Sprint health: **{health}**\n"
        f"- Carryover risk: {ctx.get('carryover_risk_count', 0)} task(s) at risk\n\n"
        f"**Team load (story points):**\n"
        + "\n".join(f"- {o}: {p} pts" for o, p in load.items())
    )


def _answer_risks(ctx: Dict) -> str:
    risks = ctx.get("risks_summary", [])
    critical = ctx.get("critical_risks", [])
    high = ctx.get("high_risks", [])
    if not risks:
        return "No open risks found."
    lines = [f"**{len(risks)} open risk(s):**\n"]
    if critical:
        lines.append("**Critical:**")
        for r in critical[:3]:
            lines.append(f"- {r}")
    if high:
        lines.append("\n**High:**")
        for r in high[:3]:
            lines.append(f"- {r}")
    lines.append(f"\n**Top mitigation:** {risks[0].get('mitigation', 'See risk registry.')}")
    return "\n".join(lines)


def _answer_okrs(ctx: Dict) -> str:
    okrs = ctx.get("okrs", [])
    at_risk = ctx.get("at_risk_okrs", [])
    unaligned = ctx.get("unaligned_work_pct", 0)
    if not okrs:
        return "No OKR data available."
    lines = [f"**OKR Status — {len(okrs)} Objectives:**\n"]
    for o in okrs:
        avg = round(sum(kr["progress"] for kr in o["krs"]) / len(o["krs"]), 1) if o["krs"] else 0
        lines.append(f"- **{o['id']}**: {o['objective']} — {o['status']} ({avg:.0f}% avg KR progress)")
    if at_risk:
        lines.append(f"\n**At risk:** {', '.join(at_risk)}")
    if unaligned > 15:
        lines.append(f"\n**Warning:** {unaligned:.0f}% of active work has no OKR link.")
    return "\n".join(lines)


def _answer_focus(ctx: Dict) -> str:
    blockers = ctx.get("open_blockers", [])
    critical = ctx.get("critical_risks", [])
    at_risk = ctx.get("at_risk_okrs", [])
    bottlenecks = ctx.get("bottleneck_owners", [])
    lines = ["**This week's recommended focus for the PM:**\n"]
    priority = 1
    if blockers:
        lines.append(f"{priority}. **Unblock** {len(blockers)} stuck/blocked task(s). "
                     "Lead today's standup with blockers first.")
        priority += 1
    if critical:
        lines.append(f"{priority}. **Escalate critical risk:** {critical[0]}")
        priority += 1
    if at_risk:
        lines.append(f"{priority}. **Review OKR recovery plan** for {', '.join(at_risk)}.")
        priority += 1
    if bottlenecks:
        lines.append(f"{priority}. **Address bottleneck:** {', '.join(bottlenecks)} has multiple blocked tasks — "
                     "redistribute or escalate.")
        priority += 1
    if ctx.get("sprint_health") in ("At Risk", "Needs Attention"):
        lines.append(f"{priority}. **Sprint re-scope:** Sprint velocity is below target. "
                     "Consider deferring low-priority tasks to Sprint 8.")
    return "\n".join(lines)


def _answer_retro(ctx: Dict) -> str:
    points = ctx.get("retro_points", [])
    sprint = ctx.get("active_sprint", "current sprint")
    lines = [f"**Retrospective talking points for {sprint}:**\n"]
    if points:
        for p in points:
            lines.append(f"- {p}")
    else:
        lines.append("- Review sprint velocity and commitment accuracy.")
        lines.append("- Discuss any recurring blockers or dependency issues.")
        lines.append("- Identify one process improvement to commit to next sprint.")
    lines.append(
        "\n*Tip: Use a Start/Stop/Continue or 4Ls format. "
        "Timebox to 90 minutes for a 2-week sprint.*"
    )
    return "\n".join(lines)


def _answer_capacity(ctx: Dict) -> str:
    overloaded = ctx.get("overloaded_owners", [])
    task_counts = ctx.get("team_task_counts", {})
    blocked_counts = ctx.get("team_blocked_counts", {})
    lines = ["**Team capacity and workload:**\n"]
    for owner, count in task_counts.items():
        blocked = blocked_counts.get(owner, 0)
        flag = " ⚠️ OVERLOADED" if owner in overloaded else ""
        blocked_str = f" ({blocked} blocked)" if blocked > 0 else ""
        lines.append(f"- {owner}: {count} active tasks{blocked_str}{flag}")
    if overloaded:
        lines.append(f"\n**Action:** {', '.join(overloaded)} should be priority focus for "
                     "blocker resolution or task redistribution.")
    return "\n".join(lines)


def _answer_overdue(ctx: Dict) -> str:
    overdue = ctx.get("overdue_tasks", [])
    if not overdue:
        return "No overdue tasks detected."
    lines = [f"**{len(overdue)} overdue task(s):**\n"]
    for t in overdue[:5]:
        lines.append(f"- **{t['name']}** (owner: {t['owner']}, due: {t['due']})")
    lines.append("\n**Action:** Review each overdue task for a new realistic due date or "
                 "escalate to the sprint re-scope discussion.")
    return "\n".join(lines)


def _answer_general(ctx: Dict) -> str:
    return (
        f"**Smart PMO Agent — Project Summary**\n\n"
        f"- Health: **{ctx.get('health_score', 'Unknown')}**\n"
        f"- Active sprint: {ctx.get('active_sprint', 'N/A')} ({ctx.get('sprint_health', 'N/A')})\n"
        f"- Velocity: {ctx.get('sprint_velocity', 0):.0%} of plan\n"
        f"- Open risks: {ctx.get('risk_count', 0)}\n"
        f"- OKRs at risk: {', '.join(ctx.get('at_risk_okrs', [])) or 'None'}\n\n"
        "Try asking: 'What should I focus on this week?' or 'What are the current blockers?'"
    )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _extract_data_points(ctx: Dict) -> List[str]:
    points = []
    if ctx.get("health_score"):
        points.append(f"Health: {ctx['health_score']}")
    if ctx.get("risk_count"):
        points.append(f"{ctx['risk_count']} open risks")
    if ctx.get("at_risk_okrs"):
        points.append(f"At-risk OKRs: {', '.join(ctx['at_risk_okrs'])}")
    return points


def _format_context_for_prompt(ctx: Dict) -> str:
    lines = [
        f"Health: {ctx.get('health_score')} — {ctx.get('health_summary')}",
        f"Sprint: {ctx.get('active_sprint')} | Velocity: {ctx.get('sprint_velocity', 0):.0%} | "
        f"Health: {ctx.get('sprint_health')}",
        f"Blockers: {len(ctx.get('open_blockers', []))} open",
        f"Risks: {ctx.get('risk_count', 0)} open | Critical: {', '.join(ctx.get('critical_risks', [])) or 'None'}",
        f"OKRs at risk: {', '.join(ctx.get('at_risk_okrs', [])) or 'None'}",
        f"Overloaded owners: {', '.join(ctx.get('overloaded_owners', [])) or 'None'}",
        f"Unaligned work: {ctx.get('unaligned_work_pct', 0):.0f}%",
    ]
    return "\n".join(lines)
