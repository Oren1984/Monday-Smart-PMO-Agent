from __future__ import annotations

from typing import List

from src.core.contracts import OKRAlignmentReport, PMOOKR, PMOTask


def analyze_okr_alignment(okrs: List[PMOOKR], tasks: List[PMOTask]) -> OKRAlignmentReport:
    """
    Compute task-to-OKR alignment across all tasks.
    Identifies unaligned work, at-risk OKRs, and per-OKR task mappings.
    """
    active_tasks = [t for t in tasks if t.status not in ("Done",)]
    total_active = len(active_tasks)

    # Map each OKR to its contributing active tasks
    okr_task_map: dict = {o.id: [] for o in okrs}
    unaligned: List[PMOTask] = []

    for t in active_tasks:
        if t.okr_link and t.okr_link in okr_task_map:
            okr_task_map[t.okr_link].append(t)
        else:
            unaligned.append(t)

    unaligned_pct = round((len(unaligned) / total_active * 100), 1) if total_active > 0 else 0.0

    at_risk = [o for o in okrs if o.status in ("At Risk", "Off Track")]

    summary = _build_summary(okrs, unaligned, unaligned_pct, at_risk)

    return OKRAlignmentReport(
        okrs=okrs,
        unaligned_task_count=len(unaligned),
        unaligned_task_pct=unaligned_pct,
        at_risk_okrs=at_risk,
        okr_task_map=okr_task_map,
        summary=summary,
    )


def get_okr_avg_kr_progress(okr: PMOOKR) -> float:
    """Return average key result progress (0–100) for an OKR."""
    if not okr.key_results:
        return 0.0
    return round(sum(kr.progress_pct for kr in okr.key_results) / len(okr.key_results), 1)


def _build_summary(okrs: List[PMOOKR], unaligned: List[PMOTask],
                   unaligned_pct: float, at_risk: List[PMOOKR]) -> str:
    parts = []
    if at_risk:
        names = ", ".join(o.id for o in at_risk)
        parts.append(f"{len(at_risk)} OKR(s) at risk or off track: {names}.")
    else:
        parts.append("All OKRs on track.")
    if unaligned_pct > 20:
        parts.append(
            f"{unaligned_pct:.0f}% of active work is not linked to any OKR. "
            "Consider reviewing sprint backlog alignment."
        )
    elif unaligned_pct > 0:
        parts.append(
            f"{unaligned_pct:.0f}% of active work is unaligned (maintenance/ops tasks)."
        )
    return " ".join(parts)
