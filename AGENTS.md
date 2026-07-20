# AGENTS.md — Monday Smart PMO Agent

This file describes how an AI coding agent should understand and work on this project.

---

## Project Role

**Monday Smart PMO Agent** is an AI-powered PMO assistant focused on:

- Portfolio visibility
- Risk monitoring
- Sprint insights
- OKR alignment analysis
- Executive reporting

The agent helps project managers and PMO stakeholders understand portfolio status, detect risks early, summarize sprint progress, identify team overload, and align work with strategic OKRs.

---

## Goal

Help project managers and PMO stakeholders:

- Understand portfolio status at a glance
- Detect risks before they become critical failures
- Summarize sprint progress and health
- Identify team overload and capacity imbalances
- Align daily work with OKRs and business goals
- Generate executive-level PMO summaries

---

## Inputs

The system accepts the following data types:

- Monday-style project and task data (boards, tasks, statuses, owners, due dates)
- Sprint data (velocity, planned vs. completed points, sprint health)
- Team workload data (per-owner task counts, story points, blocked tasks)
- Risk data (risk registry with severity, probability, impact, mitigations)
- OKR data (objectives, key results, progress, status, task-to-OKR mapping)
- PM methodology and governance notes (Agile, Scrum, OKR framework, capacity management)
- Future: live Monday API data via the integration adapter

---

## Outputs

The system produces the following outputs:

- Portfolio status summaries (health score, blockers, sprint progress)
- Risk insights (risk registry sorted by severity, mitigation recommendations)
- Sprint health insights (velocity, team load, retro talking points, carryover risk)
- Team load insights (per-owner distribution, overload detection, bottlenecks)
- OKR alignment insights (at-risk OKRs, unaligned work percentage, KR progress)
- Executive-level PMO summaries (portfolio-wide view with key signals and recommended actions)
- Recommended follow-up actions (for human PM/PMO review and approval)

---

## Constraints

- The system does not make final project decisions.
- The system does not approve or reject work automatically.
- The system does not replace a PM, PMO lead, product owner, or engineering manager.
- Human approval is required for decisions, escalations, reprioritization, and operational changes.
- All additions must remain lightweight and understandable.
- No unnecessary dependencies should be introduced.

---

## Success Criteria

A change or addition to this project is successful when:

- The project remains runnable in demo mode (no API key or Monday account required).
- The demo clearly shows PMO value to a project manager or PMO stakeholder.
- The architecture shows mock/demo mode as active and future real Monday API as a planned extension.
- The system demonstrates Human-in-the-Loop thinking — the agent suggests, the human decides.
- The project avoids over-engineering (no multi-agent, no MCP server, no cloud deploy required).

---

## Coding Rules

When contributing to this project:

- Prefer small, clear modules over large frameworks.
- Do not introduce large dependencies (no LangChain, no LlamaIndex, no heavy orchestration).
- Do not add unnecessary dependencies to `requirements.txt`.
- Preserve existing demo behavior — do not break the Streamlit app.
- Keep UI language simple and PM-oriented (avoid technical RAG terminology in the UI).
- Use mock/demo data unless real API configuration is explicitly provided via environment variables.
- Any future Monday API code must be isolated behind the integration adapter (`src/integrations/`).
- Do not hardcode API tokens or credentials — use environment variables only.
- Do not add comments explaining what the code does — prefer clear naming. Add a comment only when the WHY is non-obvious.

---

## Integration Architecture

The project uses an adapter pattern for data access:

```
src/integrations/
├── __init__.py              # Factory: get_monday_client()
├── monday_client_base.py    # Abstract interface for all Monday clients
├── monday_mock_client.py    # Active: loads local demo JSON data
└── monday_api_client.py     # Future placeholder: raises NotImplementedError
```

**Rule:** All new data access must go through `MondayClientBase`. Never read raw JSON files directly from outside the integrations layer.

**Future Monday API:** Implement by completing `monday_api_client.py`. Use only:
- `MONDAY_API_TOKEN` environment variable for authentication
- `MONDAY_WORKSPACE_ID` environment variable for workspace selection

No hardcoded values. No real credentials in the codebase.

---

## PMO Analysis Modules

```
src/pmo/project_health.py     # Portfolio health score (Green/Yellow/Red)
src/pmo/sprint_analyzer.py    # Sprint velocity, health, retro points
src/pmo/capacity_tracker.py   # Per-owner workload, overload detection
src/risk/risk_detector.py     # Risk registry, severity sorting
src/okr/okr_analyzer.py       # OKR alignment, KR progress, unaligned work
```

Each module accepts typed DTOs (from `src/core/contracts.py`) and returns typed result objects. Keep this pattern — no UI dependencies inside analysis modules.

---

## Key Capabilities (Skills)

| Capability | Module |
|-----------|--------|
| Sprint Analysis | `src/pmo/sprint_analyzer.py` |
| Risk Analysis | `src/risk/risk_detector.py` |
| Team Load Analysis | `src/pmo/capacity_tracker.py` |
| OKR Alignment Analysis | `src/okr/okr_analyzer.py` |
| Executive Summary | `src/pmo/project_health.py` + `src/reporting/report_builder.py` |
| AI PMO Q&A | `src/pipeline/pmo_pipeline.py` |

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PMO_DATA_SOURCE` | `mock` | `mock` = demo mode, `monday_api` = live Monday |
| `EMBEDDING_PROVIDER` | `mock` | `mock`, `huggingface`, `openai`, `gemini` |
| `OPENAI_API_KEY` | empty | Enables full AI Q&A (optional) |
| `MONDAY_API_TOKEN` | empty | Future: live Monday integration |
| `MONDAY_WORKSPACE_ID` | empty | Future: Monday workspace selection |

Demo mode works with all defaults — no environment configuration required.

---

## What NOT to Change

- Do not rename integration files (`monday_client_base.py`, `monday_mock_client.py`, `monday_api_client.py`) — they follow the established adapter pattern.
- Do not move demo data out of `data/monday_demo/` — the mock client depends on this location.
- Do not add real Monday credentials to any file in the repository.
- Do not change the existing Pydantic DTOs in `src/core/contracts.py` without reviewing all downstream consumers.
- Do not add a real MCP server, multi-agent framework, or cloud deployment unless explicitly requested and scoped.
