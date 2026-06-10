"""End-to-end test — full demo data load → analysis → AI Q&A mock."""
from __future__ import annotations

import pytest

from src.integrations import get_monday_client
from src.okr.okr_analyzer import analyze_okr_alignment
from src.pmo.capacity_tracker import analyze_capacity
from src.pmo.project_health import analyze_project_health
from src.pmo.sprint_analyzer import analyze_sprint
from src.reporting.report_builder import build_pmo_context
from src.risk.risk_detector import get_open_risks


@pytest.fixture(scope="module")
def full_context():
    client = get_monday_client(data_source="mock", data_dir="data/monday_demo")
    tasks = client.get_tasks()
    sprints = client.get_sprints()
    risks = client.get_risks()
    okrs = client.get_okrs()
    active = next((s for s in sprints if s.status == "active"), None)

    health = analyze_project_health(tasks, active)
    sprint_report = analyze_sprint(active, tasks) if active else None
    capacity = analyze_capacity(tasks)
    okr_report = analyze_okr_alignment(okrs, tasks)
    open_risks = get_open_risks(risks)

    ctx = build_pmo_context(
        health=health, sprint_report=sprint_report,
        risks=open_risks, okr_report=okr_report,
        capacity=capacity, active_sprint=active, all_tasks=tasks,
    )
    return ctx


class TestFullDemoFlow:
    def test_context_has_health(self, full_context):
        assert "health_score" in full_context
        assert full_context["health_score"] in ("Green", "Yellow", "Red")

    def test_context_has_sprint(self, full_context):
        assert "active_sprint" in full_context
        assert full_context["active_sprint"] != "N/A"

    def test_context_has_risks(self, full_context):
        assert "risk_count" in full_context
        assert full_context["risk_count"] >= 0

    def test_context_has_okrs(self, full_context):
        assert "okrs" in full_context
        assert len(full_context["okrs"]) >= 2

    def test_context_has_team_load(self, full_context):
        assert "team_load" in full_context
        assert len(full_context["team_load"]) > 0

    def test_mock_ai_answers_health_question(self, full_context):
        from src.pipeline.pmo_pipeline import _answer_health
        answer = _answer_health(full_context)
        assert "Health" in answer
        assert len(answer) > 20

    def test_mock_ai_answers_blocker_question(self, full_context):
        from src.pipeline.pmo_pipeline import _answer_blockers
        answer = _answer_blockers(full_context)
        assert len(answer) > 10

    def test_mock_ai_answers_focus_question(self, full_context):
        from src.pipeline.pmo_pipeline import _answer_focus
        answer = _answer_focus(full_context)
        assert "focus" in answer.lower() or "week" in answer.lower() or "priorit" in answer.lower()

    def test_mock_ai_answers_sprint_question(self, full_context):
        from src.pipeline.pmo_pipeline import _answer_sprint
        answer = _answer_sprint(full_context)
        assert "Sprint" in answer or "velocity" in answer.lower()

    def test_all_context_values_serializable(self, full_context):
        import json
        serialized = json.dumps(full_context)
        assert len(serialized) > 100
