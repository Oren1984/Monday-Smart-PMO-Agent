from __future__ import annotations

from typing import List, Optional

from src.core.contracts import PMOSprint, PMOTask, SprintReport


def analyze_sprint(sprint: PMOSprint, tasks: List[PMOTask]) -> SprintReport:
    """
    Compute a SprintReport for the given sprint and its tasks.

    Velocity:
      >= 0.75 -> Healthy
      0.50 – 0.74 -> Needs Attention
      < 0.50 -> At Risk
    """
    sprint_tasks = [t for t in tasks if t.sprint == sprint.name]

    by_status = _split_by_status(sprint_tasks)

    velocity = 0.0
    if sprint.planned_points > 0:
        velocity = round(sprint.completed_points / sprint.planned_points, 3)

    health = _velocity_health(velocity)

    team_load = _compute_team_load(sprint_tasks)
    bottlenecks = _find_bottlenecks(sprint_tasks, threshold=2)

    carryover_risk = [
        t for t in sprint_tasks
        if t.status in ("Stuck", "Blocked", "In Progress")
    ]

    retro_points = _generate_retro_points(
        sprint, sprint_tasks, velocity, bottlenecks, by_status
    )

    return SprintReport(
        sprint=sprint,
        velocity=velocity,
        health=health,
        tasks_done=by_status["Done"],
        tasks_in_progress=by_status["In Progress"],
        tasks_stuck=by_status["Stuck"],
        tasks_blocked=by_status["Blocked"],
        tasks_todo=by_status["To Do"],
        team_load=team_load,
        bottleneck_owners=bottlenecks,
        carryover_risk_tasks=carryover_risk,
        retro_points=retro_points,
    )


def _split_by_status(tasks: List[PMOTask]) -> dict:
    result: dict = {"Done": [], "In Progress": [], "Stuck": [], "Blocked": [], "To Do": []}
    for t in tasks:
        result.setdefault(t.status, []).append(t)
        if t.status not in result:
            result["To Do"].append(t)
    return result


def _velocity_health(velocity: float) -> str:
    if velocity >= 0.75:
        return "Healthy"
    if velocity >= 0.50:
        return "Needs Attention"
    return "At Risk"


def _compute_team_load(tasks: List[PMOTask]) -> dict:
    load: dict = {}
    for t in tasks:
        load[t.owner] = load.get(t.owner, 0) + t.story_points
    return dict(sorted(load.items(), key=lambda x: x[1], reverse=True))


def _find_bottlenecks(tasks: List[PMOTask], threshold: int = 2) -> List[str]:
    blocked_counts: dict = {}
    for t in tasks:
        if t.status in ("Stuck", "Blocked"):
            blocked_counts[t.owner] = blocked_counts.get(t.owner, 0) + 1
    return [owner for owner, count in blocked_counts.items() if count >= threshold]


def _generate_retro_points(sprint: PMOSprint, tasks: List[PMOTask],
                            velocity: float, bottlenecks: List[str],
                            by_status: dict) -> List[str]:
    points = []

    if velocity < 0.5:
        points.append(
            f"Sprint velocity was {velocity:.0%} of plan — review sprint capacity "
            "and dependency mapping at next planning session."
        )

    blocked_count = len(by_status.get("Blocked", [])) + len(by_status.get("Stuck", []))
    if blocked_count > 2:
        points.append(
            f"{blocked_count} tasks were stuck or blocked. Consider a daily "
            "blocker stand-up to surface impediments faster."
        )

    if bottlenecks:
        owners_str = ", ".join(bottlenecks)
        points.append(
            f"{owners_str} had multiple blocked tasks. Review workload "
            "distribution and consider cross-training or pairing."
        )

    # Carryover tasks
    carryover = [t for t in tasks if t.status not in ("Done",)]
    if carryover:
        points.append(
            f"{len(carryover)} task(s) did not complete this sprint. "
            "Review sprint commitment size and dependency health at planning."
        )

    # Check for previous retro notes to acknowledge improvements
    if sprint.retro_notes:
        points.append(
            "Review previous sprint retro actions for follow-through before "
            "identifying new improvements."
        )

    if not points:
        points.append(
            "Sprint completed cleanly. Use retrospective to document what "
            "practices contributed to the healthy velocity."
        )

    return points
