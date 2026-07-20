# Governance, Security & Observability — Monday Smart PMO Agent

This is the single authoritative governance reference for the project. It replaces the
former `AI_GOVERNANCE_AND_RISK_PRINCIPLES.md` and `security_observability.md`, whose
content has been merged and corrected here.

---

## 1. Governance Scope

Governance in this project means: clear boundaries on what the system is allowed to do,
transparent decision logic, and mandatory human review before anything derived from the
system's output affects a real project.

**Governed:** the PMO analysis engine's outputs (health scores, risk registry, sprint
health, OKR alignment, capacity flags), the AI Q&A assistant's answers, data handling in
mock mode, and credential hygiene.

**Intentionally outside scope:** production deployment, multi-user access control, live
write-back to Monday, and enterprise compliance tooling. None of these exist in the
codebase today, and none are needed for the project's current purpose — a local,
single-user, mock-data portfolio demonstration of PMO analysis and AI-assisted reporting.

Governance here does not require enterprise infrastructure because the system does not
act on anything. It reads local demo data, computes deterministic scores, and displays
them. There is no write path, no external account, and no shared state between users.
Governance is implemented through:

- Clear boundaries (read-only, single-user, local)
- Transparent rules (hardcoded, documented thresholds — see Section 3)
- Human approval (the PM decides; the tool advises)
- Audit-friendly outputs (every score traces to a named file and a test)
- Security hygiene (no hardcoded secrets, environment-variable-only credentials)
- Documentation accuracy (this document is kept in sync with the code it describes)
- Controlled use of AI (advisory only, always labeled as such in demo mode)

---

## 2. Human-in-the-Loop

The system provides analysis and recommendations. It does not autonomously execute
business decisions.

- The user (PM, PMO lead, engineering manager) remains responsible for every approval.
- The system does not reassign tasks.
- The system does not change task or sprint statuses.
- The system does not escalate risks or OKR gaps automatically to any stakeholder.
- The system does not write back to Monday in any way — `MondayAPIClient` is an
  unimplemented placeholder (see Section 4).
- The system does not perform automatic remediation of any detected risk or blocker.

**Where human review is expected:** every risk escalation, every reprioritization,
every reassignment of work, every OKR target or delivery-timeline change, and any
external communication of project status. The Executive Dashboard, Risks & Blockers,
Sprint Health, OKR Alignment, and Capacity tabs are all designed to be read by a human
who then decides what to do — none of them contain an action button that changes
underlying data.

---

## 3. Decision Boundaries

### Deterministic decisions

Produced by transparent, hardcoded Python business rules:

| Decision | Module |
|---|---|
| Project health score (Green/Yellow/Red) | `src/pmo/project_health.py` |
| Sprint health (Healthy / Needs Attention / At Risk) | `src/pmo/sprint_analyzer.py` |
| Capacity / overload detection | `src/pmo/capacity_tracker.py` |
| Risk severity ordering | `src/risk/risk_detector.py` |
| OKR alignment and unaligned-work percentage | `src/okr/okr_analyzer.py` |

These are unit-tested (`tests/unit/`), independent of any LLM, and are the
authoritative source for every score and status shown in the UI. See
`docs/architecture.md` for the exact thresholds.

### AI-generated explanations

Produced by `PMOPipeline` (`src/pipeline/pmo_pipeline.py`) — either the OpenAI-backed
path (`_openai_answer`, active only if `OPENAI_API_KEY` is set) or the rule-based mock
path (`_mock_answer`, active by default, keyword-routed to one of 9 response
generators).

AI-generated text:

- Does not override any business rule above.
- Does not modify a score, health status, or risk severity.
- Does not trigger any action — it only returns a `PMOAnswer` string for display.
- Must be treated as advisory. Mock-mode answers explicitly append a disclosure line
  ("This is a demo response...").
- May require human verification, especially the OpenAI path, which is a general
  language model and can be wrong or incomplete despite grounding context.

---

## 4. Security

- **Mock-first architecture.** Default `PMO_DATA_SOURCE=mock` requires no external
  account, no API token, and no network access.
- **No required production credentials.** `OPENAI_API_KEY`, `GEMINI_API_KEY`,
  `MONDAY_API_TOKEN`, and `MONDAY_WORKSPACE_ID` are all optional and empty by default.
- **`.env` is excluded from Git** via `.gitignore` and was confirmed not present in the
  tracked file list or in `git log --all` history.
- **Real tokens must never be committed.** `.env.example` contains placeholders only —
  every value is empty.
- **No secret appears in documentation, tests, screenshots, logs, or sample files** —
  verified by repository-wide search.
- **Local `.env` files must not be included when the project folder is zipped, copied,
  exported, or shared by any means other than `git clone`/`git push` of tracked
  content.** If a local `.env` has a real Monday token set (as it may during
  development), rotate or clear it before sharing the folder as a raw copy.
- **Live integration is not implemented.** `MondayAPIClient`
  (`src/integrations/monday_api_client.py`) unconditionally raises
  `NotImplementedError` for every method regardless of what credentials are supplied.
- **Input boundary validation** (`src/security/`):
  - `file_validation.py` — rejects files over `MAX_UPLOAD_MB` (default 10MB) or outside
    the allowed extension set (`.txt`, `.pdf`, `.html`, `.htm`).
  - `query_validation.py` — rejects empty or oversized query text before it is embedded.
  - `prompt_safety.py` — logs a warning for suspicious query patterns (prompt-injection
    style phrasing); this is advisory logging only, it does not block the query.
  - `pii_redaction.py` — optional pattern-based redaction (emails, phone numbers, basic
    name patterns) available for document ingestion; not exhaustive, not a substitute
    for a dedicated PII service.
- **Docker runs as a non-root user** (`appuser`, set in `Dockerfile`).
- **The current risk surface is limited** because the system is local, single-user, and
  read-only — there is no network-facing write path to secure.

This project does **not** claim enterprise-grade security certification, SOC/ISO
compliance, or production hardening. Those are explicitly out of scope (Section 12).

---

## 5. Read-Only and Action Safety

The current project is read-only by design:

- It performs analysis only — no data mutation of any kind.
- It does not update Monday, in mock mode or (if ever implemented) live mode.
- It does not execute project-management decisions.
- It does not make autonomous operational changes.
- It contains no automatic-approval flow.
- It contains no auto-remediation mechanism.

This is an intentional safety boundary, not a missing feature. A tool that only reads
and summarizes cannot cause an operational incident by itself — every consequential
action still requires a human to act outside the tool.

---

## 6. Monitoring

What actually exists today, verified against the code:

| Capability | Implemented in | Visible in UI? | Persistent or in-memory? | Notes |
|---|---|---|---|---|
| Pipeline counters (`documents_loaded_total`, `chunks_created_total`, `query_count_total`, `error_count_total`) | `src/observability/metrics.py` (`METRICS` singleton) | No | In-memory only, resets on restart | Updated by `PMOPipeline` during indexing/query; not read by `app/streamlit_app.py` today |
| Latency tracking (`embedding_latency_seconds`, `retrieval_latency_seconds`, `rerank_latency_seconds`) | `src/observability/metrics.py` | No | In-memory only | Same as above — internal instrumentation, not surfaced |
| Readiness checks (`check_health()` / `HealthStatus`) | `src/observability/health.py` | No | Computed on call, not persisted | Not imported or called anywhere in `app/streamlit_app.py` — a standalone utility available for a future health surface, not currently wired in |
| Error logging | `src/core/logging_config.py`, standard Python logging | No dedicated UI panel; visible in terminal/console where Streamlit runs | Not persisted | `prompt_safety.py` warnings and pipeline exceptions log through this |
| Test results | `pytest` (59 tests) | No | Run on demand | The nearest thing to a "status board" this project has — green tests are the health signal |

**There is no "System Status" tab or equivalent in the UI.** The 7 real tabs are
Executive Dashboard, Sprint Health, Risks & Blockers, OKR Alignment, Capacity, AI PMO
Assistant, and About (`app/streamlit_app.py`). All monitoring described above is
internal-only and suitable for local demo/debugging use, not production observability.

This project does not integrate Prometheus, Grafana, OpenTelemetry, ELK, or any
external monitoring service.

---

## 7. Observability

**Monitoring** (Section 6) answers "is a specific known thing OK right now" via
counters and checks. **Observability** is the broader ability to understand *why* the
system produced a given output — which this project achieves primarily through code
transparency and tests rather than runtime telemetry.

What exists:

- Application logs via `src/core/logging_config.py`
- The `METRICS` counters and latencies described above (internal only)
- Deterministic, human-readable rule outputs (health scores, risk explanations) that
  trace directly to named functions in `src/pmo/`, `src/risk/`, `src/okr/`
- 59 passing tests (`tests/unit/`, `tests/integration/`, `tests/e2e/`) that document
  expected behavior for every analysis module
- Traceable calculations — every score in the UI can be walked back to a specific
  Python function and its unit test
- Typed exception classes (`src/core/exceptions.py`) that name the failure category
  (`ConfigurationError`, `ValidationError`, `IntegrationError`, `PMOAnalysisError`,
  `AIQueryError`, etc.) rather than raising generic errors

What is intentionally absent, because this is a local mock/demo system:

- No distributed tracing
- No production telemetry pipeline
- No centralized log aggregation
- No external alerting (PagerDuty, email, Slack, etc.)
- No long-term metric retention — `METRICS` resets on every process restart
- No production incident-management process

---

## 8. Auditability and Traceability

For any result shown in the UI, a reviewer can trace it as follows:

1. **Which input produced it** — all inputs are typed DTOs in `src/core/contracts.py`
   (`PMOTask`, `PMOSprint`, `PMORisk`, `PMOOKR`), normalized from
   `data/monday_demo/*.json` by `MondayMockClient`.
2. **Which deterministic rule produced a score** — the module listed in Section 3's
   table (e.g., a health score always comes from `src/pmo/project_health.py`).
3. **Which threshold was used** — documented in `docs/architecture.md` (e.g., "Green —
   <15% tasks blocked/stuck AND sprint ≥55% complete").
4. **Which file contains the rule** — same table as above; there is one module per
   analysis concern, no cross-cutting logic to untangle.
5. **Which test validates the behavior** — `tests/unit/test_project_health.py`,
   `test_risk_detector.py`, `test_okr_analyzer.py`; `tests/integration/` for the full
   pipeline; `tests/e2e/` for the end-to-end demo flow.
6. **Which result came from business logic vs. the AI layer** — business-rule outputs
   (scores, statuses, counts) come from `src/pmo/`/`src/risk/`/`src/okr/` and are always
   deterministic; free-text explanations and Q&A answers come from `PMOPipeline` and are
   always labeled with a `mode` field (`"mock"`, `"openai"`, or `"error"`) on the
   returned `PMOAnswer`.

The system favors explainability over opaque automation: every number on the dashboard
has a one-hop path back to the exact line of code that produced it.

---

## 9. Cost Awareness

**Current cost model (mock mode, the default):**

- No Monday API requirement — zero cost.
- No cloud hosting — runs locally via `streamlit run` or `docker compose up`.
- No Kubernetes, managed database, message queue, or enterprise monitoring cost.
- No mandatory LLM API cost — `EMBEDDING_PROVIDER=mock` and no `OPENAI_API_KEY` means
  the entire demo runs with $0 in API spend.

**If `OPENAI_API_KEY` is set (optional):** the AI assistant uses `gpt-4o-mini`. Per
`docs/api_keys_guide.md`, a typical demo session costs under $0.01. This is the only
place in the project where real-world cost can be incurred, and it is opt-in.

**Future cost controls — required only if live integration is ever approved:**

- API usage limits and rate limiting on any live Monday or LLM calls
- Explicit model selection (avoid defaulting to the most expensive model)
- Token limits per request
- Response/embedding caching to avoid redundant calls
- Usage monitoring and a defined budget threshold
- Clear cost ownership (who pays for API usage — project owner vs. client)
- A controlled trial window before any client-funded infrastructure is provisioned

This section is documentation only — no billing system or cost-tracking tooling is
implemented, and none is needed while the project stays in mock mode.

---

## 10. Privacy and Data Handling

- **Current data is entirely mock.** `data/monday_demo/*.json` describes a fictional
  company (TechCo) and product (FlowHQ) with fictional people. No real personal data is
  used or expected in the current release.
- **No data is persisted beyond the local session.** Analysis results live in Streamlit
  `session_state` only; closing the browser tab clears them. Exports (Markdown/CSV) are
  generated on demand and written only to the location the user's browser saves them —
  the application itself does not store report history on disk.
- **AI Q&A prompts and outputs are not logged or stored** beyond the in-session chat
  history shown in the AI PMO Assistant tab, which also clears on session end.
- **External services receive data only if explicitly configured:** if `OPENAI_API_KEY`
  or `GEMINI_API_KEY` is set, the relevant provider receives the question text, the
  live `pmo_context` summary, and retrieved methodology passages for that single
  request. No external service receives anything in default mock mode.

**Before introducing real organizational data, a separate review is required covering:**

- Data classification (what's sensitive, what isn't)
- Access permissions (who can see the connected Monday board)
- Retention (how long analysis results or exports are kept)
- Logging (whether prompts/outputs should be logged, and where)
- PII handling (whether `pii_redaction.py` needs to be mandatory rather than optional)
- External AI provider data-handling terms
- Any applicable legal requirements
- Explicit client approval

---

## 11. Failure Handling

The system prefers safe failure and visible errors over silent fallback or automatic
action:

| Situation | Behavior |
|---|---|
| Input data missing or malformed | Typed DTO validation and `PMOAnalysisError` (`src/core/exceptions.py`) surface the problem; the Streamlit app catches it and calls `st.error(...)` + `st.stop()` rather than rendering a partial/misleading dashboard |
| A rule cannot calculate a value (e.g., zero planned points) | Explicit zero-division guards in `project_health.py` / `sprint_analyzer.py` (covered by `test_sprint_zero_planned_no_division_error`) return a safe default instead of crashing |
| An AI response fails (OpenAI error, timeout, etc.) | `PMOPipeline.query()` catches the exception, records it via `METRICS.record_error()`, and returns "Unable to generate answer. Please try again." with `mode="error"` — never a fabricated answer |
| The RAG layer cannot retrieve useful context | Retrieval failures are caught and logged; the mock-answer path does not depend on retrieval succeeding, so the Q&A feature keeps working even if indexing failed |
| Live Monday integration is requested but not implemented | `MondayAPIClient` raises `NotImplementedError` immediately and explicitly, with a message pointing back to `PMO_DATA_SOURCE=mock` |
| A required token is missing for a mode that needs one | `ConfigurationError` is raised with a clear message (e.g., `MondayAPIClient` requires `MONDAY_API_TOKEN`) rather than proceeding with a null credential |
| A feature is outside current scope | Documented here and in `docs/known_limitations.md` rather than partially implemented |

No failure path in this codebase falls back to taking an autonomous action — every
failure either stops safely or degrades to a clearly labeled advisory response.

---

## 12. Governance Limitations

This project does **not** provide, and makes no claim to provide:

- Enterprise IAM
- SSO
- Full role-based access control (RBAC)
- Production compliance certification (SOC 2, ISO 27001, etc.)
- SIEM integration
- SOC (security operations center) integration
- Distributed tracing
- Production incident-response process
- Cloud deployment controls
- Automated policy enforcement
- Live Monday synchronization
- Autonomous remediation
- Automated approvals
- Multi-agent governance
- MCP (Model Context Protocol) governance
- Regulatory compliance guarantees of any kind

Listing these explicitly is intentional — it prevents this project's documentation from
implying capabilities that would overstate its maturity in a portfolio context.

---

## 13. Future Reopening Conditions

Governance-related engineering should only be expanded if one of the following occurs:

- A real client requires live Monday integration.
- Real organizational data will be used (triggering the Section 10 review).
- The system moves toward any production or multi-user deployment.
- Write-back functionality to Monday is explicitly requested and scoped.
- Multiple users or roles are introduced.
- External hosting is approved.
- Compliance requirements are defined by a client or stakeholder.
- A measurable security risk is found in the current implementation.
- A core business rule (Section 3) is proven incorrect.

Until one of these occurs, this document — and the governance posture it describes —
should remain unchanged.
