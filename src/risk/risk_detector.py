from __future__ import annotations

from typing import List, Optional

from src.core.contracts import (
    CapacityReport,
    PMOOKR,
    PMORisk,
    PMOSprint,
    PMOTask,
    ProjectHealthReport,
    SprintReport,
)

_LEVEL_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def get_open_risks(risks: List[PMORisk]) -> List[PMORisk]:
    """Return open risks sorted by severity."""
    open_risks = [r for r in risks if r.status == "Open"]
    return sorted(open_risks, key=lambda r: _LEVEL_ORDER.get(r.level, 99))


def enrich_risks_with_analysis(
    risks: List[PMORisk],
    health: Optional[ProjectHealthReport] = None,
    sprint_report: Optional[SprintReport] = None,
    capacity: Optional[CapacityReport] = None,
    okrs: Optional[List[PMOOKR]] = None,
) -> List[PMORisk]:
    """
    Optionally generate additional derived risks from live analysis data.
    These are runtime-detected risks added on top of the pre-defined risks.json.
    """
    derived: List[PMORisk] = []

    # Detect capacity-derived risk not already in pre-defined risks
    if capacity:
        for owner in capacity.overloaded_owners:
            blocked = capacity.owner_blocked_counts.get(owner, 0)
            if blocked >= 2:
                derived.append(PMORisk(
                    id=f"AUTO-{owner.replace(' ', '_')}",
                    title=f"Capacity overload detected — {owner}",
                    description=(
                        f"{owner} has {capacity.owner_task_counts.get(owner, 0)} active tasks "
                        f"including {blocked} blocked/stuck. Risk of delivery slip."
                    ),
                    level="High",
                    probability="High",
                    impact="Medium",
                    mitigation="Redistribute tasks or escalate blockers immediately.",
                    owner="PM",
                    status="Open",
                ))

    combined = risks + derived
    return sorted(combined, key=lambda r: _LEVEL_ORDER.get(r.level, 99))


def summarize_risk_level(risks: List[PMORisk]) -> str:
    """Return the highest severity level among open risks."""
    open_risks = [r for r in risks if r.status == "Open"]
    if not open_risks:
        return "Low"
    for level in ("Critical", "High", "Medium", "Low"):
        if any(r.level == level for r in open_risks):
            return level
    return "Low"
