# Testing Strategy — Smart PMO Agent

## Overview

Tests are organized in three layers. All layers run in mock mode — no API key,
Monday account, or external service is required.

```bash
pytest                    # all tests
pytest tests/unit/        # unit tests
pytest tests/integration/ # integration tests
pytest tests/e2e/         # end-to-end flow
pytest --cov=src          # with coverage
```

---

## Unit Tests (tests/unit/)

Test individual analysis functions in isolation using hand-crafted fixtures.

| File | What is tested |
|------|---------------|
| `test_project_health.py` | Health scoring, status counts, overdue detection, blocker detection, sprint progress |
| `test_risk_detector.py` | Risk filtering, severity sorting, empty inputs |
| `test_okr_analyzer.py` | Task-to-OKR mapping, unaligned work calculation, at-risk OKR detection, KR progress |

Key rules:
- All tests use minimal in-memory fixture data (no JSON files)
- Each test asserts a specific, predictable output
- Edge cases: empty lists, zero divisions, missing optional fields

---

## Integration Tests (tests/integration/)

Test that the MondayMockClient loads real demo data correctly and that the full analysis
pipeline produces consistent results.

| File | What is tested |
|------|---------------|
| `test_pmo_pipeline.py` | Client loading, DTO shape, sprint filter, all 5 analysis modules run end-to-end |

Key rules:
- Uses real `data/monday_demo/*.json` files
- Asserts structural correctness (right types, valid status values)
- Asserts that risk sorting is stable

---

## End-to-End Tests (tests/e2e/)

Run the full demo data → analysis → context build → mock AI answer pipeline.

| File | What is tested |
|------|---------------|
| `test_full_demo_flow.py` | Full context dict built correctly, all mock answer generators work, context is JSON-serializable |

---

## What Never Requires API Keys

| Component | Reason |
|-----------|--------|
| Unit tests | Use in-memory fixtures only |
| Integration tests | Use MondayMockClient (local JSON) |
| E2E tests | Use mock analysis and mock answer generators |
| Streamlit UI startup | Mock mode is the default |
| Docker container | `PMO_DATA_SOURCE=mock` in default `.env` |

---

## Test Coverage Goals

| Module | Target |
|--------|--------|
| `src/pmo/project_health.py` | > 95% |
| `src/pmo/sprint_analyzer.py` | > 90% |
| `src/risk/risk_detector.py` | > 95% |
| `src/okr/okr_analyzer.py` | > 95% |
| `src/integrations/monday_mock_client.py` | > 85% |
| `src/reporting/report_builder.py` | > 85% |
| `src/pipeline/pmo_pipeline.py` (mock path) | > 80% |
