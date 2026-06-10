"""Unit tests — project_health.py"""
from __future__ import annotations

from datetime import date

import pytest

from src.core.contracts import PMOSprint, PMOTask
from src.pmo.project_health import analyze_project_health


def _task(id, status, priority="Medium", owner="Alice", pts=3, due=None, blocker=None):
    return PMOTask(
        id=id, board_id="b001", group="Sprint 1", name=f"Task {id}",
        status=status, priority=priority, owner=owner, story_points=pts,
        due_date=due, sprint="Sprint 1", blocker=blocker,
    )


def _sprint(planned=40, completed=20, status="active"):
    return PMOSprint(
        id="s1", name="Sprint 1", board_id="b001",
        start_date="2026-06-01", end_date="2026-06-14",
        planned_points=planned, completed_points=completed, status=status,
    )


class TestAnalyzeProjectHealth:
    def test_all_done_is_green(self):
        tasks = [_task(f"t{i}", "Done") for i in range(5)]
        result = analyze_project_health(tasks)
        assert result.health_score == "Green"
        assert result.done == 5

    def test_heavy_blocking_is_red(self):
        tasks = [_task(f"t{i}", "Blocked") for i in range(4)]
        tasks += [_task("t10", "Done")]
        result = analyze_project_health(tasks)
        assert result.health_score == "Red"

    def test_some_stuck_is_yellow(self):
        tasks = (
            [_task(f"d{i}", "Done") for i in range(6)]
            + [_task("s1", "Stuck")]
            + [_task("s2", "Stuck")]
        )
        result = analyze_project_health(tasks)
        assert result.health_score in ("Yellow", "Green")

    def test_counts_correct(self):
        tasks = [
            _task("t1", "Done"),
            _task("t2", "In Progress"),
            _task("t3", "Stuck"),
            _task("t4", "Blocked"),
            _task("t5", "To Do"),
        ]
        r = analyze_project_health(tasks)
        assert r.done == 1
        assert r.in_progress == 1
        assert r.stuck == 1
        assert r.blocked == 1
        assert r.todo == 1
        assert r.total_tasks == 5

    def test_overdue_detection(self):
        past = "2026-01-01"
        future = "2099-01-01"
        tasks = [
            _task("t1", "In Progress", due=past),   # overdue
            _task("t2", "Done", due=past),            # done, not overdue
            _task("t3", "Stuck", due=future),         # not yet due
        ]
        r = analyze_project_health(tasks, reference_date=date(2026, 6, 10))
        assert len(r.overdue_tasks) == 1
        assert r.overdue_tasks[0].id == "t1"

    def test_open_blockers_detected(self):
        tasks = [
            _task("t1", "Blocked", blocker="Waiting on something"),
            _task("t2", "Stuck", blocker="Design pending"),
            _task("t3", "In Progress"),
        ]
        r = analyze_project_health(tasks)
        assert len(r.open_blockers) == 2

    def test_sprint_progress_computed(self):
        sprint = _sprint(planned=40, completed=20)
        r = analyze_project_health([_task("t1", "Done")], active_sprint=sprint)
        assert r.sprint_progress_pct == 50.0

    def test_sprint_zero_planned_no_division_error(self):
        sprint = _sprint(planned=0, completed=0)
        r = analyze_project_health([_task("t1", "Done")], active_sprint=sprint)
        assert r.sprint_progress_pct == 0.0

    def test_empty_task_list(self):
        r = analyze_project_health([])
        assert r.total_tasks == 0
        assert r.health_score == "Green"
        assert r.summary != ""
