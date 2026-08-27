"""Unit tests — capacity_tracker.py"""
from __future__ import annotations

from src.core.contracts import PMOTask
from src.pmo.capacity_tracker import analyze_capacity


def _task(id, owner, status="In Progress", pts=3):
    return PMOTask(
        id=id, board_id="b1", group="Sprint 1", name=f"Task {id}",
        status=status, priority="Medium", owner=owner, story_points=pts,
    )


class TestAnalyzeCapacity:
    def test_done_tasks_excluded(self):
        tasks = [_task("t1", "Alice", status="Done"), _task("t2", "Alice")]
        cap = analyze_capacity(tasks)
        assert cap.owner_task_counts["Alice"] == 1

    def test_overload_detected(self):
        tasks = [_task(f"t{i}", "Alice") for i in range(5)]
        cap = analyze_capacity(tasks)
        assert "Alice" in cap.overloaded_owners

    def test_underload_detected(self):
        tasks = [_task("t1", "Alice"), _task("t2", "Bob"), _task("t3", "Bob")]
        cap = analyze_capacity(tasks)
        assert "Alice" in cap.underloaded_owners

    def test_blocked_counts_tracked(self):
        tasks = [_task("t1", "Alice", status="Blocked"), _task("t2", "Alice")]
        cap = analyze_capacity(tasks)
        assert cap.owner_blocked_counts["Alice"] == 1

    def test_empty_tasks_no_error(self):
        cap = analyze_capacity([])
        assert cap.owner_task_counts == {}
        assert cap.concentration_risk_owners == []


class TestConcentrationRisk:
    def test_owner_over_40pct_flagged(self):
        # Alice: 12 pts, Bob: 4 pts, Carol: 4 pts -> Alice holds 60% of 20 total
        tasks = [
            _task("t1", "Alice", pts=12),
            _task("t2", "Bob", pts=4),
            _task("t3", "Carol", pts=4),
        ]
        cap = analyze_capacity(tasks)
        assert cap.concentration_risk_owners == ["Alice"]

    def test_evenly_split_not_flagged(self):
        tasks = [
            _task("t1", "Alice", pts=5),
            _task("t2", "Bob", pts=5),
            _task("t3", "Carol", pts=5),
        ]
        cap = analyze_capacity(tasks)
        assert cap.concentration_risk_owners == []

    def test_zero_points_no_division_error(self):
        tasks = [_task("t1", "Alice", pts=0)]
        cap = analyze_capacity(tasks)
        assert cap.concentration_risk_owners == []
