from __future__ import annotations

from datetime import date
from typing import List, Optional

from src.core.contracts import PMOSprint, PMOTask, ProjectHealthReport


def analyze_project_health(tasks: List[PMOTask],
                            active_sprint: Optional[PMOSprint] = None,
                            reference_date: Optional[date] = None) -> ProjectHealthReport:
    """
    Compute a ProjectHealthReport from a list of tasks.

    Health scoring:
      Green  — < 15% tasks blocked/stuck AND sprint >= 55% complete
      Yellow — 15–30% blocked/stuck OR sprint 35–54% complete
      Red    — > 30% blocked/stuck OR sprint < 35% complete
    """
    today = reference_date or date.today()

    # Count by status
    status_counts = _count_by_status(tasks)
    total = len(tasks)
    done = status_counts.get("Done", 0)
    in_progress = status_counts.get("In Progress", 0)
    stuck = status_counts.get("Stuck", 0)
    blocked = status_counts.get("Blocked", 0)
    todo = status_counts.get("To Do", 0)

    # Overdue tasks (not Done, has due_date, due_date < today)
    overdue = [
        t for t in tasks
        if t.status not in ("Done",)
        and t.due_date
        and _parse_date(t.due_date) < today
    ]

    # Open blockers (Blocked or Stuck with a blocker field)
    open_blockers = [
        t for t in tasks
        if t.status in ("Blocked", "Stuck") and t.blocker
    ]

    # Sprint progress
    sprint_pct = 0.0
    if active_sprint and active_sprint.planned_points > 0:
        sprint_pct = round(
            (active_sprint.completed_points / active_sprint.planned_points) * 100, 1
        )

    # Health score
    blocked_pct = ((stuck + blocked) / total * 100) if total > 0 else 0
    health_score = _compute_health(blocked_pct, sprint_pct)

    # Summary
    summary = _build_summary(health_score, total, done, stuck, blocked,
                              overdue, open_blockers, sprint_pct, active_sprint)

    return ProjectHealthReport(
        health_score=health_score,
        total_tasks=total,
        done=done,
        in_progress=in_progress,
        stuck=stuck,
        blocked=blocked,
        todo=todo,
        overdue_tasks=overdue,
        open_blockers=open_blockers,
        sprint_progress_pct=sprint_pct,
        summary=summary,
    )


def _count_by_status(tasks: List[PMOTask]) -> dict:
    counts: dict = {}
    for t in tasks:
        counts[t.status] = counts.get(t.status, 0) + 1
    return counts


def _compute_health(blocked_pct: float, sprint_pct: float) -> str:
    if blocked_pct > 30 or (sprint_pct > 0 and sprint_pct < 35):
        return "Red"
    if blocked_pct > 15 or (sprint_pct > 0 and sprint_pct < 55):
        return "Yellow"
    return "Green"


def _build_summary(health: str, total: int, done: int, stuck: int,
                   blocked: int, overdue: list, blockers: list,
                   sprint_pct: float, sprint: Optional[PMOSprint]) -> str:
    sprint_name = sprint.name if sprint else "active sprint"
    parts = []
    if sprint_pct > 0:
        parts.append(f"{sprint_name} is {sprint_pct:.0f}% complete.")
    parts.append(f"{done} of {total} tasks done.")
    if stuck + blocked > 0:
        parts.append(f"{stuck + blocked} task(s) stuck or blocked.")
    if overdue:
        parts.append(f"{len(overdue)} overdue task(s).")
    if health == "Red":
        parts.append("Immediate attention required.")
    elif health == "Yellow":
        parts.append("Monitor closely — risks present.")
    else:
        parts.append("Project on track.")
    return " ".join(parts)


def _parse_date(date_str: str) -> date:
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return date.max
