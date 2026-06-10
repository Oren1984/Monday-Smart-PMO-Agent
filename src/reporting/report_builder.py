from __future__ import annotations

from typing import Dict, List, Optional

from src.core.contracts import (
    CapacityReport,
    OKRAlignmentReport,
    PMOOKR,
    PMORisk,
    PMOSprint,
    PMOTask,
    ProjectHealthReport,
    SprintReport,
)


def build_pmo_context(
    health: ProjectHealthReport,
    sprint_report: Optional[SprintReport],
    risks: List[PMORisk],
    okr_report: OKRAlignmentReport,
    capacity: CapacityReport,
    active_sprint: Optional[PMOSprint],
    all_tasks: List[PMOTask],
) -> Dict:
    """
    Assemble a single PMO context dictionary used by the AI Q&A pipeline
    and the Streamlit UI. Summarizes all analysis results into a flat,
    readable structure.
    """
    ctx: Dict = {}

    # Project health
    ctx["health_score"] = health.health_score
    ctx["health_summary"] = health.summary
    ctx["total_tasks"] = health.total_tasks
    ctx["done"] = health.done
    ctx["in_progress"] = health.in_progress
    ctx["stuck"] = health.stuck
    ctx["blocked"] = health.blocked
    ctx["todo"] = health.todo
    ctx["sprint_progress_pct"] = health.sprint_progress_pct
    ctx["overdue_count"] = len(health.overdue_tasks)
    ctx["overdue_tasks"] = [
        {"id": t.id, "name": t.name, "owner": t.owner, "due": t.due_date}
        for t in health.overdue_tasks
    ]
    ctx["open_blockers"] = [
        {"id": t.id, "name": t.name, "owner": t.owner, "blocker": t.blocker}
        for t in health.open_blockers
    ]

    # Sprint
    if sprint_report:
        ctx["active_sprint"] = sprint_report.sprint.name
        ctx["sprint_goal"] = sprint_report.sprint.goal
        ctx["sprint_velocity"] = sprint_report.velocity
        ctx["sprint_health"] = sprint_report.health
        ctx["sprint_team"] = sprint_report.sprint.team
        ctx["sprint_planned_pts"] = sprint_report.sprint.planned_points
        ctx["sprint_completed_pts"] = sprint_report.sprint.completed_points
        ctx["team_load"] = sprint_report.team_load
        ctx["bottleneck_owners"] = sprint_report.bottleneck_owners
        ctx["retro_points"] = sprint_report.retro_points
        ctx["carryover_risk_count"] = len(sprint_report.carryover_risk_tasks)
    else:
        ctx["active_sprint"] = "N/A"

    # Risks
    open_risks = [r for r in risks if r.status == "Open"]
    ctx["risk_count"] = len(open_risks)
    ctx["critical_risks"] = [r.title for r in open_risks if r.level == "Critical"]
    ctx["high_risks"] = [r.title for r in open_risks if r.level == "High"]
    ctx["risks_summary"] = [
        {
            "id": r.id, "title": r.title, "level": r.level,
            "mitigation": r.mitigation, "affected_okr": r.affected_okr,
        }
        for r in open_risks
    ]

    # OKRs
    ctx["okr_summary"] = okr_report.summary
    ctx["at_risk_okrs"] = [o.id for o in okr_report.at_risk_okrs]
    ctx["unaligned_work_pct"] = okr_report.unaligned_task_pct
    ctx["okrs"] = [
        {
            "id": o.id,
            "objective": o.objective,
            "owner": o.owner,
            "status": o.status,
            "krs": [
                {"id": kr.id, "desc": kr.description,
                 "progress": kr.progress_pct, "status": kr.status}
                for kr in o.key_results
            ],
        }
        for o in okr_report.okrs
    ]

    # Capacity
    ctx["overloaded_owners"] = capacity.overloaded_owners
    ctx["team_task_counts"] = capacity.owner_task_counts
    ctx["team_blocked_counts"] = capacity.owner_blocked_counts

    return ctx
