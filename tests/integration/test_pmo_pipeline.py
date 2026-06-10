"""Integration tests — MondayMockClient and PMO analysis pipeline."""
from __future__ import annotations

import pytest

from src.integrations import get_monday_client
from src.okr.okr_analyzer import analyze_okr_alignment
from src.pmo.capacity_tracker import analyze_capacity
from src.pmo.project_health import analyze_project_health
from src.pmo.sprint_analyzer import analyze_sprint
from src.risk.risk_detector import get_open_risks


@pytest.fixture(scope="module")
def client():
    return get_monday_client(data_source="mock", data_dir="data/monday_demo")


@pytest.fixture(scope="module")
def pmo_data(client):
    return {
        "tasks": client.get_tasks(),
        "sprints": client.get_sprints(),
        "risks": client.get_risks(),
        "okrs": client.get_okrs(),
    }


class TestMondayMockClient:
    def test_boards_loaded(self, client):
        boards = client.get_boards()
        assert len(boards) >= 1
        assert all(b.id and b.name for b in boards)

    def test_tasks_loaded(self, pmo_data):
        tasks = pmo_data["tasks"]
        assert len(tasks) >= 10
        assert all(t.id and t.name and t.status and t.owner for t in tasks)

    def test_sprints_loaded(self, pmo_data):
        sprints = pmo_data["sprints"]
        assert len(sprints) >= 2
        active = [s for s in sprints if s.status == "active"]
        assert len(active) == 1

    def test_risks_loaded(self, pmo_data):
        risks = pmo_data["risks"]
        assert len(risks) >= 3
        assert all(r.level in ("Critical", "High", "Medium", "Low") for r in risks)

    def test_okrs_loaded(self, pmo_data):
        okrs = pmo_data["okrs"]
        assert len(okrs) >= 2
        assert all(len(o.key_results) > 0 for o in okrs)

    def test_sprint_filter(self, client):
        sprint_tasks = client.get_tasks(sprint="Sprint 7")
        assert all(t.sprint == "Sprint 7" for t in sprint_tasks)


class TestPMOAnalysis:
    def test_project_health_runs(self, pmo_data):
        tasks = pmo_data["tasks"]
        active = next((s for s in pmo_data["sprints"] if s.status == "active"), None)
        h = analyze_project_health(tasks, active)
        assert h.health_score in ("Green", "Yellow", "Red")
        assert h.total_tasks == len(tasks)
        assert h.done + h.in_progress + h.stuck + h.blocked + h.todo == h.total_tasks

    def test_sprint_analysis_runs(self, pmo_data):
        active = next(s for s in pmo_data["sprints"] if s.status == "active")
        sr = analyze_sprint(active, pmo_data["tasks"])
        assert sr.velocity >= 0.0
        assert sr.health in ("Healthy", "Needs Attention", "At Risk")
        assert sr.sprint.name == active.name

    def test_capacity_analysis_runs(self, pmo_data):
        cap = analyze_capacity(pmo_data["tasks"])
        assert len(cap.owner_task_counts) > 0
        assert all(v >= 0 for v in cap.owner_task_counts.values())

    def test_okr_alignment_runs(self, pmo_data):
        r = analyze_okr_alignment(pmo_data["okrs"], pmo_data["tasks"])
        assert r.unaligned_task_pct >= 0.0
        assert len(r.okrs) == len(pmo_data["okrs"])

    def test_risk_detection_returns_sorted(self, pmo_data):
        risks = get_open_risks(pmo_data["risks"])
        levels = [r.level for r in risks]
        order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        assert all(
            order.get(levels[i], 99) <= order.get(levels[i+1], 99)
            for i in range(len(levels)-1)
        )
