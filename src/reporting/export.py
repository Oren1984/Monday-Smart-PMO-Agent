"""
Export utilities for the Smart PMO Agent.

Generates local CSV and Markdown reports from analysis results.
All exports are in-memory strings — no files written to disk.
The Streamlit UI passes them directly to st.download_button.
"""
from __future__ import annotations

import csv
import io
from datetime import date
from typing import List, Optional

from src.core.contracts import (
    OKRAlignmentReport,
    PMORisk,
    ProjectHealthReport,
    SprintReport,
)
from src.okr.okr_analyzer import get_okr_avg_kr_progress


def sprint_summary_csv(sprint_report: SprintReport) -> str:
    """CSV with every sprint task: ID, name, status, priority, owner, points, epic, OKR, blocker."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Task ID", "Task Name", "Status", "Priority",
        "Owner", "Story Points", "Epic", "OKR Link",
        "Due Date", "Blocker",
    ])
    all_tasks = (
        sprint_report.tasks_done
        + sprint_report.tasks_in_progress
        + sprint_report.tasks_stuck
        + sprint_report.tasks_blocked
        + sprint_report.tasks_todo
    )
    for t in all_tasks:
        writer.writerow([
            t.id, t.name, t.status, t.priority,
            t.owner, t.story_points, t.epic or "",
            t.okr_link or "", t.due_date or "",
            (t.blocker or "").replace("\n", " "),
        ])
    return buf.getvalue()


def risk_registry_csv(risks: List[PMORisk]) -> str:
    """CSV with all open risks: ID, title, level, probability, impact, owner, OKR, mitigation."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Risk ID", "Title", "Level", "Probability",
        "Impact", "Status", "Owner",
        "Affected OKR", "Affected Sprint", "Mitigation",
    ])
    for r in risks:
        writer.writerow([
            r.id, r.title, r.level, r.probability,
            r.impact, r.status, r.owner,
            r.affected_okr or "", r.affected_sprint or "",
            r.mitigation.replace("\n", " "),
        ])
    return buf.getvalue()


def project_health_markdown(
    health: ProjectHealthReport,
    sprint_report: Optional[SprintReport],
    risks: List[PMORisk],
    okr_report: OKRAlignmentReport,
    report_date: Optional[date] = None,
) -> str:
    """Markdown PMO health report suitable for sharing with stakeholders."""
    today = (report_date or date.today()).isoformat()
    lines: List[str] = []

    lines += [
        f"# PMO Health Report — {today}",
        "",
        f"**Project Health:** {health.health_score}",
        "",
        health.summary,
        "",
        "---",
        "",
        "## Task Status",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| Done | {health.done} |",
        f"| In Progress | {health.in_progress} |",
        f"| Stuck | {health.stuck} |",
        f"| Blocked | {health.blocked} |",
        f"| To Do | {health.todo} |",
        f"| **Total** | **{health.total_tasks}** |",
        "",
    ]

    if health.overdue_tasks:
        lines += ["## Overdue Tasks", ""]
        for t in health.overdue_tasks:
            lines.append(f"- **{t.name}** — {t.owner} (due: {t.due_date})")
        lines.append("")

    if health.open_blockers:
        lines += ["## Active Blockers", ""]
        for t in health.open_blockers:
            lines.append(f"- **{t.name}** — {t.owner}")
            lines.append(f"  > {t.blocker}")
        lines.append("")

    if sprint_report:
        sr = sprint_report
        lines += [
            "---",
            "",
            f"## Sprint: {sr.sprint.name}",
            "",
            f"**Goal:** {sr.sprint.goal}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Health | {sr.health} |",
            f"| Velocity | {sr.velocity:.0%} |",
            f"| Points | {sr.sprint.completed_points} / {sr.sprint.planned_points} |",
            f"| Carryover Risk | {len(sr.carryover_risk_tasks)} task(s) |",
            "",
        ]
        if sr.bottleneck_owners:
            lines.append(f"**Bottlenecks:** {', '.join(sr.bottleneck_owners)}")
            lines.append("")
        if sr.retro_points:
            lines += ["**Retrospective Notes:**", ""]
            for p in sr.retro_points:
                lines.append(f"- {p}")
            lines.append("")

    open_risks = [r for r in risks if r.status == "Open"]
    if open_risks:
        lines += [
            "---",
            "",
            f"## Risks ({len(open_risks)} open)",
            "",
            "| ID | Title | Level | Affected OKR |",
            "|----|-------|-------|-------------|",
        ]
        for r in open_risks:
            lines.append(f"| {r.id} | {r.title} | {r.level} | {r.affected_okr or '—'} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## OKR Status",
        "",
    ]
    for okr in okr_report.okrs:
        avg = get_okr_avg_kr_progress(okr)
        lines.append(f"### {okr.id} — {okr.objective}")
        lines.append(f"**Status:** {okr.status} | **Owner:** {okr.owner} | "
                     f"**Avg KR Progress:** {avg:.0f}%")
        lines.append("")
        for kr in okr.key_results:
            lines.append(f"- {kr.id}: {kr.description} — "
                         f"{kr.current} / {kr.target} {kr.unit} ({kr.status})")
        lines.append("")

    if okr_report.unaligned_task_pct > 0:
        lines.append(f"**Unaligned work:** {okr_report.unaligned_task_pct:.0f}% of active tasks "
                     "have no OKR link.")
        lines.append("")

    lines += [
        "---",
        "",
        "*Generated by Smart PMO Agent — local Monday-style demo data.*",
        "*Real Monday API integration is a planned future extension.*",
    ]

    return "\n".join(lines)
