"""Unit tests — src/reporting/export.py"""
from __future__ import annotations

import csv
import io

import pytest

from src.core.contracts import (
    CapacityReport,
    OKRAlignmentReport,
    PMOKeyResult,
    PMOOKR,
    PMORisk,
    PMOSprint,
    PMOTask,
    ProjectHealthReport,
    SprintReport,
)
from src.reporting.export import (
    project_health_markdown,
    risk_registry_csv,
    sprint_summary_csv,
)


# ── Fixtures ──────────────────────────────────────────────────────────────

def _task(id, status="In Progress", owner="Alice", pts=3, epic="Onboarding",
          okr_link="OKR-1", due=None, blocker=None):
    return PMOTask(
        id=id, board_id="b1", group="Sprint 1", name=f"Task {id}",
        status=status, priority="Medium", owner=owner, story_points=pts,
        due_date=due, sprint="Sprint 1", epic=epic, okr_link=okr_link,
        blocker=blocker,
    )


def _sprint_report():
    sprint = PMOSprint(
        id="s1", name="Sprint 1", board_id="b1",
        start_date="2026-06-01", end_date="2026-06-14",
        planned_points=30, completed_points=18, status="active",
        goal="Ship onboarding v2",
    )
    return SprintReport(
        sprint=sprint,
        velocity=0.60,
        health="Needs Attention",
        tasks_done=[_task("t1", "Done")],
        tasks_in_progress=[_task("t2", "In Progress")],
        tasks_stuck=[_task("t3", "Stuck", blocker="Waiting on Design")],
        tasks_blocked=[_task("t4", "Blocked", blocker="Schema not ready")],
        tasks_todo=[_task("t5", "To Do")],
        team_load={"Alice": 10, "Bob": 8},
        bottleneck_owners=["Alice"],
        carryover_risk_tasks=[_task("t3", "Stuck"), _task("t4", "Blocked")],
        retro_points=["Velocity low — review sprint capacity."],
    )


def _risk(id, level="High"):
    return PMORisk(
        id=id, title=f"Risk {id}", description="desc",
        level=level, probability="Medium", impact="High",
        mitigation="Escalate now.", owner="PM",
        status="Open", affected_okr="OKR-1",
    )


def _health():
    return ProjectHealthReport(
        health_score="Yellow",
        total_tasks=5, done=1, in_progress=1, stuck=1, blocked=1, todo=1,
        overdue_tasks=[_task("t_od", "In Progress", due="2026-01-01")],
        open_blockers=[_task("t_b", "Blocked", blocker="Schema issue")],
        sprint_progress_pct=40.0,
        summary="Sprint is 40% complete. 2 blocked/stuck tasks.",
    )


def _okr_report():
    kr = PMOKeyResult(id="KR1", description="KR 1",
                      target=100, current=60, unit="%", status="On Track")
    okr = PMOOKR(id="OKR-1", objective="Improve Onboarding",
                 owner="PM", quarter="Q2 2026", key_results=[kr], status="On Track")
    return OKRAlignmentReport(
        okrs=[okr], unaligned_task_count=1, unaligned_task_pct=20.0,
        at_risk_okrs=[], okr_task_map={"OKR-1": []},
        summary="All OKRs on track.",
    )


# ── SprintSummaryCSV ─────────────────────────────────────────────────────

class TestSprintSummaryCSV:
    def test_has_header_row(self):
        csv_str = sprint_summary_csv(_sprint_report())
        reader = csv.reader(io.StringIO(csv_str))
        header = next(reader)
        assert "Task ID" in header
        assert "Status" in header
        assert "Owner" in header

    def test_all_tasks_present(self):
        csv_str = sprint_summary_csv(_sprint_report())
        rows = list(csv.reader(io.StringIO(csv_str)))
        # header + 5 tasks
        assert len(rows) == 6

    def test_blocker_text_included(self):
        csv_str = sprint_summary_csv(_sprint_report())
        assert "Waiting on Design" in csv_str

    def test_empty_sprint_produces_header_only(self):
        sprint = PMOSprint(
            id="s0", name="Empty Sprint", board_id="b0",
            start_date="2026-06-01", end_date="2026-06-14",
            planned_points=0, completed_points=0, status="planned",
        )
        sr = SprintReport(sprint=sprint, velocity=0.0, health="At Risk")
        csv_str = sprint_summary_csv(sr)
        rows = list(csv.reader(io.StringIO(csv_str)))
        assert len(rows) == 1  # header only


# ── RiskRegistryCSV ──────────────────────────────────────────────────────

class TestRiskRegistryCSV:
    def test_has_header(self):
        risks = [_risk("R1"), _risk("R2", "Medium")]
        csv_str = risk_registry_csv(risks)
        reader = csv.reader(io.StringIO(csv_str))
        header = next(reader)
        assert "Risk ID" in header
        assert "Level" in header
        assert "Mitigation" in header

    def test_all_risks_present(self):
        risks = [_risk("R1"), _risk("R2"), _risk("R3")]
        csv_str = risk_registry_csv(risks)
        rows = list(csv.reader(io.StringIO(csv_str)))
        assert len(rows) == 4  # header + 3

    def test_empty_risks_produces_header_only(self):
        csv_str = risk_registry_csv([])
        rows = list(csv.reader(io.StringIO(csv_str)))
        assert len(rows) == 1


# ── ProjectHealthMarkdown ────────────────────────────────────────────────

class TestProjectHealthMarkdown:
    def test_contains_health_score(self):
        md = project_health_markdown(
            health=_health(), sprint_report=_sprint_report(),
            risks=[_risk("R1")], okr_report=_okr_report(),
        )
        assert "Yellow" in md

    def test_contains_sprint_section(self):
        md = project_health_markdown(
            health=_health(), sprint_report=_sprint_report(),
            risks=[_risk("R1")], okr_report=_okr_report(),
        )
        assert "Sprint 1" in md
        assert "Needs Attention" in md

    def test_contains_risk_table(self):
        md = project_health_markdown(
            health=_health(), sprint_report=_sprint_report(),
            risks=[_risk("R1"), _risk("R2")], okr_report=_okr_report(),
        )
        assert "R1" in md
        assert "R2" in md

    def test_contains_okr_section(self):
        md = project_health_markdown(
            health=_health(), sprint_report=_sprint_report(),
            risks=[], okr_report=_okr_report(),
        )
        assert "OKR-1" in md
        assert "Improve Onboarding" in md

    def test_no_sprint_still_renders(self):
        md = project_health_markdown(
            health=_health(), sprint_report=None,
            risks=[], okr_report=_okr_report(),
        )
        assert "PMO Health Report" in md
        assert "Yellow" in md

    def test_contains_demo_watermark(self):
        md = project_health_markdown(
            health=_health(), sprint_report=None,
            risks=[], okr_report=_okr_report(),
        )
        assert "Smart PMO Agent" in md
        assert "demo" in md.lower()

    def test_overdue_tasks_shown(self):
        md = project_health_markdown(
            health=_health(), sprint_report=None,
            risks=[], okr_report=_okr_report(),
        )
        assert "Overdue" in md

    def test_is_valid_markdown_string(self):
        md = project_health_markdown(
            health=_health(), sprint_report=_sprint_report(),
            risks=[_risk("R1")], okr_report=_okr_report(),
        )
        assert isinstance(md, str)
        assert len(md) > 200
        assert md.startswith("# PMO Health Report")
