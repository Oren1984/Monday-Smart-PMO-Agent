"""Unit tests — okr_analyzer.py"""
from __future__ import annotations

from src.core.contracts import PMOKeyResult, PMOOKR, PMOTask
from src.okr.okr_analyzer import analyze_okr_alignment, get_okr_avg_kr_progress


def _task(id, status="In Progress", okr_link=None):
    return PMOTask(
        id=id, board_id="b1", group="Sprint 1", name=f"Task {id}",
        status=status, priority="Medium", owner="Alice", story_points=3,
        okr_link=okr_link,
    )


def _okr(id, status="On Track"):
    return PMOOKR(
        id=id, objective=f"Objective {id}", owner="PM",
        quarter="Q2 2026", status=status,
        key_results=[
            PMOKeyResult(id=f"{id}-KR1", description="KR 1",
                         target=100, current=60, unit="%", status="On Track"),
            PMOKeyResult(id=f"{id}-KR2", description="KR 2",
                         target=100, current=40, unit="%", status="At Risk"),
        ],
    )


class TestAnalyzeOKRAlignment:
    def test_aligned_tasks_mapped(self):
        tasks = [_task("t1", okr_link="OKR-1"), _task("t2", okr_link="OKR-1")]
        okrs = [_okr("OKR-1")]
        r = analyze_okr_alignment(okrs, tasks)
        assert len(r.okr_task_map["OKR-1"]) == 2
        assert r.unaligned_task_count == 0

    def test_unaligned_tasks_detected(self):
        tasks = [_task("t1"), _task("t2")]  # no okr_link
        okrs = [_okr("OKR-1")]
        r = analyze_okr_alignment(okrs, tasks)
        assert r.unaligned_task_count == 2
        assert r.unaligned_task_pct == 100.0

    def test_done_tasks_excluded(self):
        tasks = [_task("t1", status="Done", okr_link="OKR-1"), _task("t2")]
        okrs = [_okr("OKR-1")]
        r = analyze_okr_alignment(okrs, tasks)
        # t1 is Done — excluded from analysis; only t2 is active
        assert r.unaligned_task_count == 1

    def test_at_risk_okrs_captured(self):
        okrs = [_okr("OKR-1", status="At Risk"), _okr("OKR-2", status="On Track")]
        r = analyze_okr_alignment(okrs, [])
        assert len(r.at_risk_okrs) == 1
        assert r.at_risk_okrs[0].id == "OKR-1"

    def test_empty_tasks_no_error(self):
        r = analyze_okr_alignment([_okr("OKR-1")], [])
        assert r.unaligned_task_count == 0
        assert r.unaligned_task_pct == 0.0


class TestGetOKRAvgKRProgress:
    def test_average_computed(self):
        okr = _okr("OKR-1")
        avg = get_okr_avg_kr_progress(okr)
        assert avg == 50.0  # (60% + 40%) / 2

    def test_no_krs_returns_zero(self):
        okr = PMOOKR(id="O1", objective="obj", owner="PM", quarter="Q2", key_results=[])
        assert get_okr_avg_kr_progress(okr) == 0.0
