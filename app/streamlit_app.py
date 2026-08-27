"""Monday Smart PMO Agent — Streamlit UI"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

st.set_page_config(
    page_title="Monday Smart PMO Agent",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📋",
)

from src.core.config import settings
from src.integrations import get_monday_client
from src.okr.okr_analyzer import analyze_okr_alignment, get_okr_avg_kr_progress
from src.reporting.export import (
    project_health_markdown,
    risk_registry_csv,
    sprint_summary_csv,
)
from src.pmo.capacity_tracker import analyze_capacity
from src.pmo.project_health import analyze_project_health
from src.pmo.sprint_analyzer import analyze_sprint
from src.reporting.report_builder import build_pmo_context
from src.risk.risk_detector import get_open_risks, summarize_risk_level

# ── Colour palette ─────────────────────────────────────────────────────────
_HEALTH_COLOUR = {"Green": "#22c55e", "Yellow": "#f59e0b", "Red": "#ef4444"}
_LEVEL_COLOUR = {
    "Critical": "#ef4444", "High": "#f97316",
    "Medium": "#f59e0b", "Low": "#22c55e",
}
_STATUS_COLOUR = {
    "Done": "#22c55e", "In Progress": "#3b82f6",
    "Stuck": "#f97316", "Blocked": "#ef4444", "To Do": "#94a3b8",
}
_OKR_COLOUR = {"On Track": "#22c55e", "At Risk": "#f59e0b", "Off Track": "#ef4444"}

# ── Session state defaults ──────────────────────────────────────────────────
_SS_DEFAULTS = {
    "pmo_data": None,
    "health": None,
    "sprint_report": None,
    "capacity": None,
    "okr_report": None,
    "risks": None,
    "pmo_context": None,
    "pmo_pipeline": None,
    "methodology_indexed": False,
    "chat_history": [],
    "selected_sprint": None,
}
for _k, _v in _SS_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Data loading ────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_pmo_data():
    client = get_monday_client(
        data_source=settings.pmo_data_source,
        data_dir=settings.monday_demo_dir,
        api_token=settings.monday_api_token,
        workspace_id=settings.monday_workspace_id,
    )
    return {
        "boards": client.get_boards(),
        "tasks": client.get_tasks(),
        "sprints": client.get_sprints(),
        "risks": client.get_risks(),
        "okrs": client.get_okrs(),
        "source_label": client.source_label,
    }


def run_analysis(data: dict, sprint_name: str | None = None):
    tasks = data["tasks"]
    sprints = data["sprints"]
    risks = data["risks"]
    okrs = data["okrs"]

    # Active sprint
    active_sprint = next((s for s in sprints if s.status == "active"), None)
    if sprint_name:
        active_sprint = next((s for s in sprints if s.name == sprint_name), active_sprint)

    health = analyze_project_health(tasks, active_sprint)
    sprint_report = analyze_sprint(active_sprint, tasks) if active_sprint else None
    capacity = analyze_capacity(tasks)
    okr_report = analyze_okr_alignment(okrs, tasks)
    open_risks = get_open_risks(risks)

    pmo_context = build_pmo_context(
        health=health,
        sprint_report=sprint_report,
        risks=open_risks,
        okr_report=okr_report,
        capacity=capacity,
        active_sprint=active_sprint,
        all_tasks=tasks,
    )

    return health, sprint_report, capacity, okr_report, open_risks, pmo_context


# ── PMO Pipeline (AI Q&A) ───────────────────────────────────────────────────

def get_pmo_pipeline():
    if st.session_state.pmo_pipeline is None:
        from src.chunking.recursive_chunker import RecursiveChunker
        from src.embeddings.mock_embedding_provider import MockEmbeddingProvider
        from src.pipeline.pmo_pipeline import PMOPipeline
        from src.retrieval.reranker import PassThroughReranker
        from src.vectorstores.chroma_store import ChromaVectorStore

        provider_name = settings.embedding_provider
        openai_key = settings.openai_api_key

        if provider_name == "huggingface":
            from src.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider
            provider = HuggingFaceEmbeddingProvider(model_name=settings.embedding_model)
        elif provider_name == "openai" and openai_key:
            from src.embeddings.openai_provider import OpenAIEmbeddingProvider
            provider = OpenAIEmbeddingProvider(api_key=openai_key, model_name=settings.embedding_model)
        else:
            provider = MockEmbeddingProvider()

        store = ChromaVectorStore(
            persist_directory=os.path.join(settings.vector_db_dir, "chroma")
        )
        chunker = RecursiveChunker(chunk_size=settings.chunk_size,
                                   chunk_overlap=settings.chunk_overlap)
        reranker = PassThroughReranker()

        pipeline = PMOPipeline(
            embedding_provider=provider,
            vector_store=store,
            chunker=chunker,
            reranker=reranker,
            openai_api_key=openai_key,
        )
        st.session_state.pmo_pipeline = pipeline

    return st.session_state.pmo_pipeline


# ══════════════════════════════════════════════════════════════════════════
# Page header
# ══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="padding:0.6rem 0 0.4rem; border-bottom:2px solid #e2e8f0; margin-bottom:0.5rem;">
  <h1 style="margin:0; font-size:1.8rem; color:#1e293b;">
    📋 Monday Smart PMO Agent
  </h1>
  <p style="margin:0.2rem 0 0; font-size:0.95rem; color:#475569;">
    AI-Powered PMO Assistant for Project Visibility, Risk Monitoring and Strategic Alignment
  </p>
</div>
""", unsafe_allow_html=True)

# ── Load data ───────────────────────────────────────────────────────────────
with st.spinner("Loading project data…"):
    try:
        pmo_data = load_pmo_data()
        st.session_state.pmo_data = pmo_data
    except Exception as e:
        st.error(f"Failed to load Monday demo data: {e}")
        st.stop()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px;
                padding:0.6rem 0.75rem; margin-bottom:0.75rem; font-size:0.82rem;">
      <strong>📡 Data Source</strong><br>
      Using local Monday-style demo data<br>
      <span style="color:#64748b;">Real Monday API integration is a future extension.</span>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Sprint Selector")
    sprint_names = [s.name for s in pmo_data["sprints"]]
    active_default = next(
        (i for i, s in enumerate(pmo_data["sprints"]) if s.status == "active"), 0
    )
    selected_sprint = st.selectbox(
        "View sprint", sprint_names, index=active_default, key="sprint_select"
    )

    st.divider()

    if st.button("🔄 Refresh Analysis", use_container_width=True):
        load_pmo_data.clear()
        for k in ["health", "sprint_report", "capacity", "okr_report",
                  "risks", "pmo_context", "methodology_indexed"]:
            st.session_state[k] = None if k != "methodology_indexed" else False
        st.rerun()

    st.divider()

    st.subheader("AI Assistant Mode")
    if settings.openai_api_key:
        st.success("OpenAI key detected — full AI responses enabled.")
        st.caption(
            "💰 Cost awareness: gpt-4o-mini, rough estimate <$0.01 per demo session. "
            "Advisory estimate only — not billing data. See docs/api_keys_guide.md."
        )
    else:
        st.info("No OpenAI key — using smart demo responses.\nAdd OPENAI_API_KEY to .env for full AI.")
        st.caption("💰 Cost awareness: $0 — offline demo mode makes no API calls.")

    st.caption(
        "🔎 **Decision Support only** — read-only, Human-in-the-Loop. "
        "The AI Assistant advises; a human PM/PMO lead decides."
    )

# ── Run analysis ─────────────────────────────────────────────────────────────
try:
    (health, sprint_report, capacity, okr_report,
     open_risks, pmo_context) = run_analysis(pmo_data, selected_sprint)
    st.session_state.update({
        "health": health, "sprint_report": sprint_report,
        "capacity": capacity, "okr_report": okr_report,
        "risks": open_risks, "pmo_context": pmo_context,
    })
except Exception as e:
    st.error(f"Analysis error: {e}")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# Tabs
# ══════════════════════════════════════════════════════════════════════════

tab_dashboard, tab_sprint, tab_risks, tab_okr, tab_capacity, tab_ai, tab_about = st.tabs([
    "📊 Executive Dashboard",
    "🏃 Sprint Health",
    "⚠️ Risks & Blockers",
    "🎯 OKR Alignment",
    "👥 Capacity",
    "🤖 AI PMO Assistant",
    "ℹ️ About",
])

# ─────────────────────────────────────────────────────────────────────────
# TAB 1 — Executive Dashboard
# ─────────────────────────────────────────────────────────────────────────
with tab_dashboard:
    st.subheader("Executive Dashboard")

    # Health badge
    hc = _HEALTH_COLOUR.get(health.health_score, "#94a3b8")
    st.markdown(f"""
    <div style="display:inline-block; background:{hc}22; border:2px solid {hc};
                border-radius:8px; padding:0.4rem 1rem; margin-bottom:0.75rem;">
      <span style="color:{hc}; font-weight:700; font-size:1.05rem;">
        Project Health: {health.health_score}
      </span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(health.summary)

    # Top metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Tasks", health.total_tasks)
    c2.metric("Done", health.done,
              delta=f"{round(health.done/health.total_tasks*100)}%" if health.total_tasks else "0%")
    c3.metric("Stuck + Blocked", health.stuck + health.blocked,
              delta=f"-{health.stuck + health.blocked}" if health.stuck + health.blocked else None,
              delta_color="inverse")
    c4.metric("Overdue", len(health.overdue_tasks),
              delta_color="inverse" if health.overdue_tasks else "normal")
    c5.metric("Open Risks", len(open_risks))

    # Sprint progress
    if sprint_report:
        st.divider()
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Active Sprint", sprint_report.sprint.name)
        sc2.metric("Sprint Progress",
                   f"{health.sprint_progress_pct:.0f}%",
                   help="Completed story points / Planned story points")
        sc3.metric("Sprint Health", sprint_report.health)
        st.progress(min(health.sprint_progress_pct / 100, 1.0),
                    text=f"{sprint_report.sprint.completed_points} / "
                         f"{sprint_report.sprint.planned_points} pts")
        if sprint_report.sprint.goal:
            st.caption(f"Sprint Goal: {sprint_report.sprint.goal}")

    # Status distribution
    st.divider()
    _c1, _c2 = st.columns(2)
    with _c1:
        st.subheader("Task Status Distribution")
        status_data = {
            "Done": health.done,
            "In Progress": health.in_progress,
            "Stuck": health.stuck,
            "Blocked": health.blocked,
            "To Do": health.todo,
        }
        for status, count in status_data.items():
            pct = (count / health.total_tasks * 100) if health.total_tasks else 0
            col = _STATUS_COLOUR.get(status, "#94a3b8")
            st.markdown(
                f'<div style="display:flex; align-items:center; margin:4px 0;">'
                f'<span style="width:110px; font-size:0.85rem;">{status}</span>'
                f'<div style="flex:1; background:#f1f5f9; border-radius:4px; height:18px; margin:0 8px;">'
                f'<div style="background:{col}; width:{pct:.0f}%; height:100%; '
                f'border-radius:4px;"></div></div>'
                f'<span style="font-size:0.85rem; width:40px; text-align:right;">{count}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with _c2:
        st.subheader("OKR Status")
        for okr in okr_report.okrs:
            avg_progress = get_okr_avg_kr_progress(okr)
            col = _OKR_COLOUR.get(okr.status, "#94a3b8")
            st.markdown(
                f'<div style="margin:6px 0; padding:6px 10px; background:#f8fafc; '
                f'border-left:4px solid {col}; border-radius:4px;">'
                f'<strong>{okr.id}</strong> — {okr.status} '
                f'<span style="color:#64748b; font-size:0.85rem;">({avg_progress:.0f}% avg KR)</span>'
                f'<br><span style="font-size:0.83rem; color:#475569;">{okr.objective[:60]}…</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Top blockers
    if health.open_blockers:
        st.divider()
        st.subheader("Active Blockers")
        for t in health.open_blockers[:4]:
            lc = _LEVEL_COLOUR.get(t.priority, "#94a3b8")
            st.markdown(
                f'<div style="padding:8px 12px; border-left:4px solid {lc}; '
                f'background:#fff7ed; margin:4px 0; border-radius:4px; font-size:0.88rem;">'
                f'<strong>{t.name}</strong> — {t.owner}<br>'
                f'<span style="color:#92400e;">{t.blocker}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Export
    st.divider()
    with st.expander("📤 Export Health Report", expanded=False):
        st.caption("Download a Markdown summary of the current project health, sprint, risks, and OKRs.")
        md_report = project_health_markdown(
            health=health,
            sprint_report=sprint_report,
            risks=open_risks,
            okr_report=okr_report,
        )
        st.download_button(
            label="⬇️ Download Health Report (.md)",
            data=md_report,
            file_name="pmo_health_report.md",
            mime="text/markdown",
            key="dl_health_md",
            use_container_width=True,
        )
        with st.expander("Preview report"):
            st.markdown(md_report)


# ─────────────────────────────────────────────────────────────────────────
# TAB 2 — Sprint Health
# ─────────────────────────────────────────────────────────────────────────
with tab_sprint:
    st.subheader("Sprint Health")
    st.caption(
        "Execution control view for the PM/Delivery Manager: sprint health, velocity, "
        "carryover risk, blockers, and capacity in one place."
    )
    if not sprint_report:
        st.info("No active sprint found in the current dataset.")
    else:
        sr = sprint_report
        hc = {"Healthy": "#22c55e", "Needs Attention": "#f59e0b", "At Risk": "#ef4444"}
        col = hc.get(sr.health, "#94a3b8")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Sprint", sr.sprint.name)
        m2.metric("Velocity", f"{sr.velocity:.0%}",
                  help="Story points completed / planned")
        m3.metric("Health", sr.health)
        m4.metric("Carryover Risk", f"{len(sr.carryover_risk_tasks)} tasks")

        st.caption(f"Goal: {sr.sprint.goal}")
        st.progress(min(sr.velocity, 1.0))
        st.caption(f"{sr.sprint.completed_points} of {sr.sprint.planned_points} story points complete · "
                   f"{sr.sprint.start_date} → {sr.sprint.end_date}")

        st.divider()
        _tc1, _tc2 = st.columns(2)

        with _tc1:
            st.subheader("Task Breakdown")
            breakdown = [
                ("Done", sr.tasks_done, "#22c55e"),
                ("In Progress", sr.tasks_in_progress, "#3b82f6"),
                ("Stuck", sr.tasks_stuck, "#f97316"),
                ("Blocked", sr.tasks_blocked, "#ef4444"),
                ("To Do", sr.tasks_todo, "#94a3b8"),
            ]
            for label, task_list, color in breakdown:
                with st.expander(f"{label} ({len(task_list)})", expanded=(label in ("Stuck", "Blocked"))):
                    for t in task_list:
                        b_text = f" · ⛔ {t.blocker[:60]}…" if t.blocker else ""
                        st.markdown(
                            f'<div style="padding:4px 0; font-size:0.85rem; border-bottom:1px solid #f1f5f9;">'
                            f'<span style="color:{color};">●</span> '
                            f'<strong>{t.name}</strong> — {t.owner} ({t.story_points}pts){b_text}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

        with _tc2:
            st.subheader("Team Load (Story Points)")
            for owner, pts in sr.team_load.items():
                is_bottleneck = owner in sr.bottleneck_owners
                icon = " ⚠️" if is_bottleneck else ""
                blocked = capacity.owner_blocked_counts.get(owner, 0)
                b_str = f" · {blocked} blocked" if blocked else ""
                st.markdown(
                    f'<div style="display:flex; align-items:center; margin:5px 0;">'
                    f'<span style="width:90px; font-size:0.85rem;">{owner}{icon}</span>'
                    f'<div style="flex:1; background:#f1f5f9; border-radius:4px; height:20px; margin:0 8px;">'
                    f'<div style="background:{"#f97316" if is_bottleneck else "#3b82f6"}; '
                    f'width:{min(pts*4, 100)}%; height:100%; border-radius:4px;"></div></div>'
                    f'<span style="font-size:0.85rem; width:70px;">{pts} pts{b_str}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        if sr.retro_points:
            st.divider()
            st.subheader("Retrospective Talking Points")
            for point in sr.retro_points:
                st.markdown(f"- {point}")

        # Previous sprint comparison
        prev_sprints = [s for s in pmo_data["sprints"] if s.status == "completed"]
        if prev_sprints:
            st.divider()
            st.subheader("Previous Sprint Comparison")
            prev = prev_sprints[-1]
            prev_vel = round(prev.completed_points / prev.planned_points, 2) if prev.planned_points else 0
            pc1, pc2, pc3 = st.columns(3)
            pc1.metric(prev.name, f"{prev_vel:.0%} velocity",
                       delta=f"{(sr.velocity - prev_vel)*100:+.0f}pp vs current")
            pc2.metric("Prev Points", f"{prev.completed_points}/{prev.planned_points}")
            pc3.metric("Prev Retro Notes", len(prev.retro_notes))
            if prev.retro_notes:
                with st.expander("Previous sprint retro notes"):
                    for note in prev.retro_notes:
                        st.markdown(f"- {note}")

    # Sprint export
    st.divider()
    with st.expander("📤 Export Sprint Summary", expanded=False):
        st.caption("Download a CSV of all tasks in the current sprint with status, owner, and points.")
        csv_data = sprint_summary_csv(sprint_report)
        st.download_button(
            label="⬇️ Download Sprint Summary (.csv)",
            data=csv_data,
            file_name=f"{sprint_report.sprint.name.replace(' ', '_')}_summary.csv",
            mime="text/csv",
            key="dl_sprint_csv",
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────
# TAB 3 — Risks & Blockers
# ─────────────────────────────────────────────────────────────────────────
with tab_risks:
    st.subheader("Risks & Blockers")

    top_level = summarize_risk_level(open_risks)
    rc = _LEVEL_COLOUR.get(top_level, "#94a3b8")
    st.markdown(
        f'<div style="display:inline-block; background:{rc}22; border:2px solid {rc}; '
        f'border-radius:8px; padding:0.35rem 1rem; margin-bottom:0.75rem;">'
        f'<span style="color:{rc}; font-weight:700;">Overall Risk Level: {top_level}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    r1, r2, r3, r4 = st.columns(4)
    for level, col_widget in [("Critical", r1), ("High", r2), ("Medium", r3), ("Low", r4)]:
        count = sum(1 for r in open_risks if r.level == level)
        col_widget.metric(level, count)

    st.divider()
    for risk in open_risks:
        lc = _LEVEL_COLOUR.get(risk.level, "#94a3b8")
        with st.expander(f"[{risk.level}] {risk.title}", expanded=(risk.level == "Critical")):
            rc1, rc2, rc3 = st.columns(3)
            rc1.markdown(f"**ID:** {risk.id}")
            rc2.markdown(f"**Owner:** {risk.owner}")
            rc3.markdown(f"**Affected OKR:** {risk.affected_okr or '—'}")
            st.markdown(f"**Description:** {risk.description}")
            st.markdown(
                f'<div style="background:#f0fdf4; border-left:3px solid #22c55e; '
                f'padding:8px 12px; border-radius:4px; margin-top:6px; font-size:0.88rem;">'
                f'<strong>Mitigation:</strong> {risk.mitigation}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Blocker detail table
    st.divider()
    st.subheader("Blocked & Stuck Tasks")
    all_blocked = [
        t for t in pmo_data["tasks"]
        if t.status in ("Blocked", "Stuck") and t.blocker
    ]
    if all_blocked:
        import pandas as pd
        df = pd.DataFrame([
            {
                "ID": t.id, "Task": t.name[:55], "Status": t.status,
                "Priority": t.priority, "Owner": t.owner,
                "Sprint": t.sprint or "—", "Blocker": (t.blocker or "")[:80],
            }
            for t in all_blocked
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("No blocked or stuck tasks at this time.")

    # Risk export
    st.divider()
    with st.expander("📤 Export Risk Registry", expanded=False):
        st.caption("Download a CSV of all open risks with severity, mitigation, and OKR impact.")
        csv_risks = risk_registry_csv(open_risks)
        st.download_button(
            label="⬇️ Download Risk Registry (.csv)",
            data=csv_risks,
            file_name="risk_registry.csv",
            mime="text/csv",
            key="dl_risks_csv",
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────
# TAB 4 — OKR Alignment
# ─────────────────────────────────────────────────────────────────────────
with tab_okr:
    st.subheader("OKR Alignment")
    st.caption(
        "Connects tactical sprint work to business objectives: which work is aligned, "
        "which is unaligned, and where execution risk (blockers) is threatening a "
        "strategic objective — not just a lagging KR number."
    )
    st.caption(okr_report.summary)

    o1, o2, o3, o4 = st.columns(4)
    o1.metric("OKRs Tracked", len(okr_report.okrs))
    o2.metric("At Risk / Off Track", len(okr_report.at_risk_okrs))
    o3.metric("Delivery Risk", len(okr_report.okrs_with_delivery_risk),
              help="At-risk OKRs whose contributing work is currently blocked or stuck")
    o4.metric("Unaligned Work", f"{okr_report.unaligned_task_pct:.0f}%",
              help="Active tasks with no OKR link")

    st.divider()
    for okr in okr_report.okrs:
        avg = get_okr_avg_kr_progress(okr)
        oc = _OKR_COLOUR.get(okr.status, "#94a3b8")
        contributing_tasks = okr_report.okr_task_map.get(okr.id, [])
        has_delivery_risk = okr.id in okr_report.okrs_with_delivery_risk
        risk_flag = " 🔥 DELIVERY RISK" if has_delivery_risk else ""

        with st.expander(
            f"{okr.id} — {okr.objective[:65]} · {okr.status} · {avg:.0f}% avg{risk_flag}",
            expanded=(okr.status != "On Track"),
        ):
            if has_delivery_risk:
                st.error(
                    "🔥 **Delivery risk to strategy:** blocked/stuck sprint work is "
                    "directly threatening this objective — this is an execution "
                    "problem, not only a lagging KR target."
                )
            oc1, oc2, oc3 = st.columns(3)
            oc1.markdown(f"**Owner:** {okr.owner}")
            oc2.markdown(f"**Quarter:** {okr.quarter}")
            oc3.markdown(f"**Contributing Tasks:** {len(contributing_tasks)}")

            st.markdown("**Key Results:**")
            for kr in okr.key_results:
                krc = _OKR_COLOUR.get(kr.status, "#94a3b8")
                pct = kr.progress_pct
                # Invert for metrics where lower = better (e.g., churn %, time)
                if "churn" in kr.description.lower() or "days" in kr.unit.lower() or "minutes" in kr.unit.lower():
                    raw_pct = pct
                    if kr.target > 0:
                        improvement = (kr.current - kr.target)
                        baseline_range = abs(kr.current - kr.target) + 0.001
                        pct = max(0, min(100, 100 - (improvement / (kr.current - kr.target + 0.001) * 100)))
                st.markdown(
                    f'<div style="margin:6px 0; padding:8px 12px; background:#f8fafc; border-radius:6px;">'
                    f'<div style="display:flex; justify-content:space-between; margin-bottom:4px;">'
                    f'<span style="font-size:0.87rem;"><strong>{kr.id}</strong>: {kr.description}</span>'
                    f'<span style="color:{krc}; font-size:0.85rem; font-weight:600;">{kr.status}</span>'
                    f'</div>'
                    f'<div style="background:#e2e8f0; border-radius:4px; height:8px;">'
                    f'<div style="background:{krc}; width:{kr.progress_pct:.0f}%; height:100%; border-radius:4px;"></div>'
                    f'</div>'
                    f'<div style="font-size:0.8rem; color:#64748b; margin-top:3px;">'
                    f'Current: {kr.current} {kr.unit} → Target: {kr.target} {kr.unit}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            if contributing_tasks:
                with st.expander(f"Contributing sprint tasks ({len(contributing_tasks)})"):
                    for t in contributing_tasks:
                        sc = _STATUS_COLOUR.get(t.status, "#94a3b8")
                        st.markdown(
                            f'<span style="color:{sc};">●</span> {t.name} — {t.owner} ({t.status})',
                            unsafe_allow_html=True,
                        )


# ─────────────────────────────────────────────────────────────────────────
# TAB 5 — Capacity
# ─────────────────────────────────────────────────────────────────────────
with tab_capacity:
    st.subheader("Team Capacity & Workload")
    st.caption(
        "Execution control view for the PM/Delivery Manager: who is overloaded, "
        "whose work is trapped by blockers, and where a single person's absence "
        "would stall delivery (bus factor)."
    )

    cap = capacity
    cc1, cc2, cc3, cc4 = st.columns(4)
    cc1.metric("Team Size", len(cap.owner_task_counts))
    cc2.metric("Overloaded", len(cap.overloaded_owners))
    cc3.metric("Bus Factor Risk", len(cap.concentration_risk_owners),
               help="Owners holding > 40% of active story points — a single point of failure.")
    cc4.metric("Total Active Tasks", sum(cap.owner_task_counts.values()))

    if cap.overloaded_owners:
        st.warning(f"⚠️ Overloaded team members: {', '.join(cap.overloaded_owners)}")
    if cap.concentration_risk_owners:
        st.error(
            f"🚌 Bus factor risk: {', '.join(cap.concentration_risk_owners)} each hold over "
            "40% of active story points. If unavailable, delivery stalls — spread this "
            "work through pairing or knowledge-sharing before it becomes a blocker."
        )

    st.divider()
    st.subheader("Workload Per Team Member")

    max_pts = max(cap.owner_point_totals.values(), default=1)

    for owner in cap.owner_task_counts:
        tasks_count = cap.owner_task_counts[owner]
        pts = cap.owner_point_totals.get(owner, 0)
        blocked = cap.owner_blocked_counts.get(owner, 0)
        is_overloaded = owner in cap.overloaded_owners
        is_concentration_risk = owner in cap.concentration_risk_owners
        bar_pct = int((pts / max_pts) * 100) if max_pts > 0 else 0
        bar_col = "#ef4444" if (is_overloaded or is_concentration_risk) else "#3b82f6"
        flag = " ⚠️" if is_overloaded else ""
        flag += " 🚌" if is_concentration_risk else ""

        st.markdown(
            f'<div style="padding:10px 14px; background:#f8fafc; border-radius:8px; '
            f'margin:6px 0; border-left:4px solid {bar_col};">'
            f'<div style="display:flex; justify-content:space-between; margin-bottom:6px;">'
            f'<strong>{owner}{flag}</strong>'
            f'<span style="font-size:0.85rem; color:#64748b;">'
            f'{tasks_count} tasks · {pts} pts · {blocked} blocked'
            f'</span>'
            f'</div>'
            f'<div style="background:#e2e8f0; border-radius:4px; height:10px;">'
            f'<div style="background:{bar_col}; width:{bar_pct}%; height:100%; border-radius:4px;"></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Per-owner task drill-down
    st.divider()
    st.subheader("Task Drill-Down by Owner")
    owner_select = st.selectbox("Select team member", list(cap.owner_task_counts.keys()))
    owner_tasks = [t for t in pmo_data["tasks"] if t.owner == owner_select and t.status != "Done"]
    if owner_tasks:
        for t in owner_tasks:
            sc = _STATUS_COLOUR.get(t.status, "#94a3b8")
            b_str = f" · ⛔ {t.blocker[:60]}" if t.blocker else ""
            st.markdown(
                f'<div style="padding:6px 10px; border-left:3px solid {sc}; '
                f'background:#f8fafc; margin:4px 0; border-radius:4px; font-size:0.85rem;">'
                f'<strong>{t.name}</strong> [{t.status}] · {t.story_points}pts'
                f'{b_str}'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.success(f"{owner_select} has no active tasks.")


# ─────────────────────────────────────────────────────────────────────────
# TAB 6 — AI PMO Assistant
# ─────────────────────────────────────────────────────────────────────────
with tab_ai:
    st.subheader("AI PMO Assistant")
    st.caption(
        "Ask questions about project status, sprint health, risks, OKRs, "
        "team workload, or what to focus on."
    )

    # Initialize pipeline and index methodology docs once
    if not st.session_state.methodology_indexed:
        with st.spinner("Indexing PM methodology documents…"):
            try:
                pipeline = get_pmo_pipeline()
                result = pipeline.index_methodology_docs(settings.methodology_docs_dir)
                st.session_state.methodology_indexed = True
                st.session_state.pmo_pipeline = pipeline
                st.toast(
                    f"Indexed {result['docs_indexed']} methodology docs "
                    f"({result['total_chunks']} chunks).",
                    icon="📚",
                )
            except Exception as e:
                st.warning(f"Methodology indexing skipped: {e}")
                st.session_state.methodology_indexed = True

    # Suggested questions
    st.markdown("**Suggested questions:**")
    suggestions = [
        "What is the current project status?",
        "Which tasks are blocking the sprint?",
        "Which OKRs are at risk?",
        "Who is overloaded on the team?",
        "What should I focus on this week?",
        "What should be discussed in the retrospective?",
    ]
    scols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        if scols[i % 3].button(suggestion, key=f"sug_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": suggestion})
            st.rerun()

    st.divider()

    # Chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask the PMO Agent…")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing…"):
                try:
                    pipeline = st.session_state.pmo_pipeline or get_pmo_pipeline()
                    answer_obj = pipeline.query(
                        user_input,
                        st.session_state.pmo_context or {},
                        top_k=settings.top_k,
                    )
                    st.markdown(answer_obj.answer)
                    if answer_obj.sources:
                        st.caption(
                            f"Methodology sources: {', '.join(answer_obj.sources)}"
                        )
                    mode_label = {
                        "mock": "Smart demo response",
                        "openai": "OpenAI GPT-4o-mini",
                        "gemini": "Gemini",
                    }.get(answer_obj.mode, answer_obj.mode)
                    st.caption(f"Mode: {mode_label} · Decision support — advisory, human review required")
                    if answer_obj.cost_note:
                        st.caption(f"💰 {answer_obj.cost_note}")
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer_obj.answer}
                    )
                except Exception as e:
                    error_msg = f"Error generating response: {e}"
                    st.error(error_msg)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": error_msg}
                    )

    if st.session_state.chat_history:
        if st.button("Clear conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────
# TAB 7 — About
# ─────────────────────────────────────────────────────────────────────────
with tab_about:
    st.subheader("About Monday Smart PMO Agent")

    st.markdown("""
**Monday Smart PMO Agent** is an AI-Powered PMO Assistant for Project Visibility, Risk Monitoring and Strategic Alignment.
It analyzes Monday-style project data and PM methodology knowledge to give project managers and PMO stakeholders
real-time visibility into portfolio health, risks, sprint performance, OKR alignment, and team workload.

> The agent supports PMO decision-making but does not replace human judgment.
> A human PM, PMO lead, or manager must approve decisions, escalations, and delivery changes.

---

### AI Governance — What the AI Layer Is

| Principle | What it means here |
|-----------|--------------------|
| **Decision Support** | The AI recommends; it never executes a decision, escalation, or reassignment |
| **Read-Only** | No write path to Monday or any data mutation exists in this system |
| **Human-in-the-Loop** | Every score, risk, and answer requires human review before acting |
| **Explainable** | Health/risk/OKR scores come from named, unit-tested rules — not the LLM |
| **Advisory, not autonomous** | Free-text answers are labeled by mode (demo / OpenAI) and never override a business rule |

See `docs/GOVERNANCE_SECURITY_OBSERVABILITY.md` for the full governance reference.

---

### Data Source

This project uses **realistic Monday-style local demo data** loaded from `data/monday_demo/`.
The data represents a fictional tech company (TechCo) building a SaaS product (FlowHQ)
with an active sprint, 8 team members, 4 OKRs, and real-looking project complexity.

**Real Monday API integration is a planned future extension.**
The architecture includes a clean adapter layer (`src/integrations/`) that allows switching
from mock data to a live Monday workspace by changing one environment setting:
```
PMO_DATA_SOURCE=monday_api
```
No other code changes are required.

---

### Five Core Flows

| Flow | What it analyzes | Output |
|------|-----------------|--------|
| **Project Visibility** | Tasks, statuses, due dates | Health score, blockers, sprint progress |
| **Risk Detection** | Blocked tasks, OKR gaps, capacity | Risk registry with mitigations |
| **Sprint Execution Control** | Velocity, carryover, blockers, capacity, bus factor | Sprint health, bottlenecks, retro talking points |
| **OKR Alignment** | Task-to-OKR mapping, blocked work on at-risk OKRs | Aligned/unaligned work, delivery risk to strategy |
| **AI PMO Q&A** | All above + methodology docs | Natural language PM answers (decision support only) |

---

### Technology Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Integration | MondayMockClient (adapter pattern) |
| PMO Analysis | Python (custom engine) |
| AI Q&A | RAG — ChromaDB + OpenAI / Mock |
| Embeddings | Mock (default) · HuggingFace · OpenAI |
| Vector Store | ChromaDB |
| Config | python-dotenv + Pydantic Settings |
| Packaging | Docker |

---

### Project Category

**Technology Project Management + AI Tools**

This project demonstrates practical AI application for project management —
not pure AI/ML engineering. It shows how a PM can use AI-powered analysis to
improve project visibility, detect risks earlier, and make better sprint decisions.
    """)
