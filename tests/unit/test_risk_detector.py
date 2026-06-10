"""Unit tests — risk_detector.py"""
from __future__ import annotations

from src.core.contracts import PMORisk
from src.risk.risk_detector import get_open_risks, summarize_risk_level


def _risk(id, level, status="Open"):
    return PMORisk(
        id=id, title=f"Risk {id}", description="desc",
        level=level, probability="Medium", impact="Medium",
        mitigation="mitigate", owner="PM", status=status,
    )


class TestGetOpenRisks:
    def test_filters_out_closed(self):
        risks = [_risk("R1", "High"), _risk("R2", "Low", status="Closed")]
        result = get_open_risks(risks)
        assert len(result) == 1
        assert result[0].id == "R1"

    def test_sorted_by_severity(self):
        risks = [_risk("R1", "Low"), _risk("R2", "Critical"), _risk("R3", "High")]
        result = get_open_risks(risks)
        assert result[0].level == "Critical"
        assert result[1].level == "High"
        assert result[2].level == "Low"

    def test_empty_returns_empty(self):
        assert get_open_risks([]) == []

    def test_all_mitigated_returns_empty(self):
        risks = [_risk("R1", "High", status="Mitigated")]
        assert get_open_risks(risks) == []


class TestSummarizeRiskLevel:
    def test_returns_highest(self):
        risks = [_risk("R1", "Medium"), _risk("R2", "Critical"), _risk("R3", "Low")]
        assert summarize_risk_level(risks) == "Critical"

    def test_no_open_returns_low(self):
        risks = [_risk("R1", "High", status="Closed")]
        assert summarize_risk_level(risks) == "Low"

    def test_empty_returns_low(self):
        assert summarize_risk_level([]) == "Low"
