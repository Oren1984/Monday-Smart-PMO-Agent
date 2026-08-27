"""Unit tests — AI cost-awareness signal in pmo_pipeline.py"""
from __future__ import annotations

from src.pipeline.pmo_pipeline import _build_cost_note


class TestBuildCostNote:
    def test_mock_mode_has_no_cost(self):
        note = _build_cost_note("mock")
        assert "No API cost" in note

    def test_openai_mode_has_estimate(self):
        note = _build_cost_note("openai")
        assert "Estimated cost" in note
        assert "not billing data" in note

    def test_error_mode_has_no_note(self):
        assert _build_cost_note("error") is None
