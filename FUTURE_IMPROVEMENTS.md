# Future Improvements

## Project Status

This project is currently **closed, stable, and should remain lean**. It runs fully in mock/demo mode with no API key or Monday account required, and 59/59 tests pass.

This document is a **future review list only**. It does not authorize implementation of anything listed below.

---

## Approved Future Review Items

### 1. Fix stale RAG-era references in `docs/security_observability.md`

- **Current issue:** The doc refers to a `RAGPipeline` class and a Streamlit "System Status tab." Neither exists in the current codebase — the active pipeline class is `PMOPipeline` (`src/pipeline/pmo_pipeline.py`), and the current UI has 7 tabs (Dashboard, Sprint Health, Risks & Blockers, OKR Alignment, Capacity/Workload, AI PMO Assistant, About) with no System Status tab. This is a leftover from the project's origin as a generic "RAG Engineering Lab" before it was repositioned as a Monday PMO tool.
- **Preferred future action:** Update the prose to reference `PMOPipeline` and remove/replace the System Status tab mention with an accurate description of where the `METRICS` singleton is actually surfaced (if anywhere in the UI today).
- **Priority:** Medium
- **Effort:** Low
- **Files involved:** `docs/security_observability.md`
- **Implementation condition:** Documentation-only edit. May proceed only after explicit human approval per the rule below.

### 2. Correct the README/config explanation of what `MONDAY_API_TOKEN` and its companion env var currently activate

- **Current issue:** `.env.example`, `AGENTS.md`, and `docs/API_KEYS_GUIDE.md` all instruct a user to set `MONDAY_BOARD_ID`, but `src/core/config.py`'s Pydantic Settings field is actually named `monday_workspace_id` (mapping to env var `MONDAY_WORKSPACE_ID`), and `src/integrations/monday_api_client.py`'s own docstring agrees with `MONDAY_WORKSPACE_ID`, not `MONDAY_BOARD_ID`. Setting either `MONDAY_API_TOKEN` or `MONDAY_BOARD_ID` today activates nothing beyond `mock` mode's default behavior — `MondayAPIClient` unconditionally raises `NotImplementedError` regardless of what credentials are supplied, since real Monday API integration is not implemented in v1.
- **Preferred future action:** When (and only when) live Monday integration is actually built, reconcile the field name and the documented env var name (rename the config field to match the docs, or vice versa), and make the README/docs explicit that setting these variables today does not enable any live data — it is inert until `monday_api_client.py` is implemented.
- **Priority:** Low
- **Effort:** Low
- **Files involved:** `src/core/config.py`, `.env.example`, `AGENTS.md`, `docs/API_KEYS_GUIDE.md`, `src/integrations/monday_api_client.py`, `README.md`
- **Implementation condition:** Bundle with real Monday API integration work if/when that is ever scoped. Not worth a standalone fix while the code path is inert.

### 3. Clarify that methodology docs and rule thresholds are reference data, not rule-engine configuration

- **Current issue:** No document currently states explicitly that `data/methodology_docs/*.md` are used only as RAG-retrieved reference text to ground the AI Q&A layer's prose (`src/pipeline/pmo_pipeline.py`), and that the actual business-rule thresholds (health scoring bands, sprint velocity bands, risk severity ordering, capacity overload detection) are hardcoded Python constants inside `src/pmo/*.py`, `src/risk/risk_detector.py`, and `src/okr/okr_analyzer.py`. A reader could reasonably but incorrectly assume the methodology docs configure the scoring logic.
- **Preferred future action:** Add a short clarifying paragraph to `docs/architecture.md` (Layer 2 / Layer 3 sections) distinguishing "business rule thresholds — hardcoded, transparent, drive scoring" from "methodology reference text — RAG-retrieved, informs AI Q&A answer prose only, does not drive scoring."
- **Priority:** Low
- **Effort:** Low
- **Files involved:** `docs/architecture.md`
- **Implementation condition:** Documentation-only edit. May proceed only after explicit human approval per the rule below.

### 4. Rotate or remove the local Monday token before the repository folder is copied, exported, zipped, or shared

- **Current issue:** The local, untracked `.env` file currently has real values set for `MONDAY_API_TOKEN` and `MONDAY_BOARD_ID`. Verification confirmed `.env` is correctly gitignored and not present anywhere in tracked files or git history (`git log --all` shows no token/credential content). The exposure risk is limited to the local filesystem — e.g., if the project folder is ever zipped, backed up, or copied to another machine by means other than `git clone`.
- **Preferred future action:** Rotate the Monday personal access token, or clear `MONDAY_API_TOKEN`/`MONDAY_BOARD_ID` in the local `.env`, before this folder is shared, exported, or archived in any way that isn't a plain `git clone`/`git push` of tracked content.
- **Priority:** High (the only item in this review with real, if narrow, security consequence)
- **Effort:** Low
- **Files involved:** local `.env` (untracked, not part of the repository)
- **Implementation condition:** Operational step, not a code change. Can be done by the project owner directly at any time without needing a code review or implementation plan.

---

## Explicitly Rejected Scope Expansion

The following should **not** be added at the current project stage:

- Kubernetes or any cloud deployment target
- Microservices split of the PMO analysis modules
- Additional databases or message queues
- Enterprise IAM / SSO / role-based access control
- Large monitoring or observability stacks (Prometheus, Grafana, OpenTelemetry, etc.)
- LLM-based risk analysis replacing the current transparent rule-based scoring
- Autonomous write-back to Monday (task reassignment, status changes, auto-escalation)
- Automatic decision execution of any kind
- Additional agents / multi-agent architecture / MCP server
- Production Monday API integration (implementing `monday_api_client.py`) without a stated business need
- Unnecessary cloud infrastructure

---

## Reopening Conditions

This project should only be reopened for active work if one of the following occurs:

- A documentation contradiction is found that materially affects portfolio credibility.
- A security issue is discovered (beyond the local-only token hygiene item above).
- A core business rule (health scoring, risk severity, OKR alignment, capacity logic) is found to be incorrect.
- The project scope changes because of a real business requirement (e.g., an actual live Monday integration is needed).
- A specific item in this document is explicitly approved by the project owner for implementation.

---

## Human Approval Rule

- No item in this file may be implemented automatically.
- Claude (or any other AI coding tool) must first prepare a proposed implementation plan before touching any file.
- The plan must identify exact files, expected changes, risks, and tests.
- Implementation may begin only after explicit human approval of that plan.
- After each approved step, the AI must stop, report the result, and wait for approval before continuing.
