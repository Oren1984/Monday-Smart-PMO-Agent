from __future__ import annotations

from typing import List

from src.core.contracts import CapacityReport, PMOTask

_OVERLOAD_THRESHOLD = 5   # tasks per person
_UNDERLOAD_THRESHOLD = 1  # tasks per person


def analyze_capacity(tasks: List[PMOTask]) -> CapacityReport:
    """
    Compute a CapacityReport showing per-owner workload and imbalances.
    Only considers active work (not Done tasks).
    """
    active = [t for t in tasks if t.status != "Done"]

    task_counts: dict = {}
    point_totals: dict = {}
    blocked_counts: dict = {}

    for t in active:
        task_counts[t.owner] = task_counts.get(t.owner, 0) + 1
        point_totals[t.owner] = point_totals.get(t.owner, 0) + t.story_points
        if t.status in ("Blocked", "Stuck"):
            blocked_counts[t.owner] = blocked_counts.get(t.owner, 0) + 1

    overloaded = [o for o, cnt in task_counts.items() if cnt >= _OVERLOAD_THRESHOLD]
    underloaded = [o for o, cnt in task_counts.items() if cnt <= _UNDERLOAD_THRESHOLD]

    return CapacityReport(
        owner_task_counts=dict(sorted(task_counts.items(), key=lambda x: x[1], reverse=True)),
        owner_point_totals=dict(sorted(point_totals.items(), key=lambda x: x[1], reverse=True)),
        owner_blocked_counts=blocked_counts,
        overloaded_owners=overloaded,
        underloaded_owners=underloaded,
    )
