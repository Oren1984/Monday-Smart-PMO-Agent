# Governance and Validation

How the tool stays advisory, how it handles security and data, how it is tested, and
what it does not do.

---

## Human Oversight

The tool informs; people decide. It surfaces signals and suggests follow-ups, and a person
(such as a project lead, delivery lead, or engineering manager) reviews them before
anything happens.

Human review is expected before:

- escalating a risk or blocker,
- re-planning or re-scoping a sprint,
- reassigning work,
- changing an OKR target or delivery timeline,
- sharing project status with others.

The Q&A assistant is instructed to recommend actions for a person to approve, never to
state that an action has been taken. Every answer is labelled with its mode and marked as
advisory decision support.

## Authority Boundaries

| The tool does | The tool does not |
|---------------|-------------------|
| Calculate health, sprint, capacity, and OKR signals | Make delivery decisions |
| List and sort open risks | Approve or reject work |
| Flag overload and blocked work | Reassign tasks or change statuses |
| Suggest follow-up actions | Escalate or notify anyone |
| Explain results in plain language | Write anything back to Monday or the data files |

The app is read-only. It has no write path to project data, no automatic approvals, and no
automatic remediation.

Scores always come from the deterministic rules in `src/pmo/`, `src/risk/`, and
`src/okr/`. AI-generated text cannot change a score, status, or severity. See
[Architecture](ARCHITECTURE.md#analysis-rules).

## Security and Privacy

**Credentials**
- Credentials are read only from environment variables or `.env`.
- `.env` is ignored by Git and excluded from the Docker build context.
- `.env.example` holds empty placeholders only.
- Default mode needs no credentials at all.
- Before sharing the project folder by any means other than Git, such as a zip or copy, clear or rotate any real tokens in your local `.env`.

**Runtime**
- The Docker container runs as a non-root user (`appuser`).
- The app is a single-user local tool with no login and no access control. It is not meant for shared or public hosting.

**Input helpers** (`src/security/`): available, but only partly used by the app.

| Helper | What it does | Used by the app? |
|--------|--------------|------------------|
| `query_validation.py` | Rejects empty or overlong (over 2,000 characters) queries | No. Used by `src/retrieval/retriever.py`, which the app does not use. The pipeline itself rejects empty questions. |
| `prompt_safety.py` | Detects suspicious prompt patterns; warns, never blocks | No |
| `file_validation.py` | Checks file size and extension (`.pdf`, `.txt`, `.md`, `.html`, `.htm`) | No (the app has no upload feature) |
| `pii_redaction.py` | Pattern-based redaction of emails, phones, and simple names | Optional in `TextCleaner`; off by default |

**Data and privacy**
- All demo data is fictional (TechCo / FlowHQ).
- Analysis results and chat history live only in the Streamlit session and are cleared when it ends. Exports are created in memory and saved only where the browser downloads them.
- In default mode nothing leaves the machine.
- With `OPENAI_API_KEY` set, each question is sent to OpenAI with a summary of the analysis results and the retrieved methodology passages. With `EMBEDDING_PROVIDER=openai`, the methodology notes and questions are sent for embedding.
- Using real organisational data would need its own review first: data classification, access, retention, logging, PII handling, and the AI provider's terms.

## Failure Handling

| Situation | Behaviour |
|-----------|-----------|
| Data cannot be loaded or analysed | The app shows an error and stops instead of rendering a partial dashboard |
| Monday API selected | Clear `ConfigurationError` or `NotImplementedError`; no silent fallback |
| Zero planned points or empty lists | Guarded calculations return safe defaults |
| OpenAI call fails | Answer reads "Unable to generate answer. Please try again." with mode `error` |
| Methodology indexing or retrieval fails | Logged; rule-based answers continue to work |

Internal counters and timings (`src/observability/metrics.py`) are kept in memory only and
are not shown in the UI. `check_health()` in `src/observability/health.py` exists but is not
called by the app. There is no external monitoring.

## Testing

All tests run offline in mock mode.

```bash
pytest                    # all tests
pytest tests/unit/        # unit tests
pytest tests/integration/ # demo data through all analysis modules
pytest tests/e2e/         # data → analysis → context → rule-based answers
pytest --cov=src          # with coverage
```

| Layer | Files | Covers |
|-------|-------|--------|
| Unit | `test_project_health.py`, `test_risk_detector.py`, `test_okr_analyzer.py`, `test_capacity_tracker.py`, `test_export.py`, `test_pmo_pipeline_cost.py` | Scoring rules, severity sorting, OKR alignment, overload and concentration, exports, cost notes, edge cases such as empty input and zero division |
| Integration | `test_pmo_pipeline.py` | Mock client loading, data shapes, sprint filter, all analysis modules on the demo data |
| End-to-end | `test_full_demo_flow.py` | Full context build, every rule-based answer type, JSON-serialisable context |

Latest local run: **73 passed**. The Streamlit UI has no automated tests; it was checked by
starting the app and viewing it in a browser.

## Limitations

- **No live data.** The Monday API client is a placeholder, and all data is static and fictional.
- **Date-dependent overdue count.** Overdue is measured against today's date, so it grows over time.
- **Rule-based answers by default.** Without an OpenAI key, answers come from keyword-matched templates.
- **Non-semantic default retrieval.** Mock embeddings are hash-based, so cited sources may not be the most relevant.
- **Optional OpenAI path.** Like any language model, it can be wrong; treat its answers as drafts to verify.
- **Single user, local.** No authentication, roles, or persistent storage, and no scheduled reports or notifications.
- **Some modules unused.** Gemini embeddings, FAISS, the retriever, and the input-safety helpers exist in `src/` but are not wired into the app.
- **No production hardening.** No compliance certification, SSO, central logging, tracing, or cloud deployment.

## Future Improvements

These are possible extensions. None are approved or implemented.

- **Live Monday integration**: implement `MondayAPIClient` with Monday's GraphQL API, using `MONDAY_API_TOKEN` and `MONDAY_WORKSPACE_ID`. This should happen only when there is a real need, with rate limits, token limits, and caching.
- **Wire in existing helpers**: apply `query_validation` and `prompt_safety` to assistant questions, and either connect or remove the unused Gemini, FAISS, and retriever modules.
- **Stable demo dates**: compute overdue against a fixed reference date in demo mode, so the figures do not drift.
- **Surface health information**: show `check_health()` and the in-memory metrics in the About tab.
- **Automated UI check**: add a smoke test that starts the app and confirms the tabs render.

Deliberately out of scope: autonomous write-back to Monday, automatic decisions or
escalations, multi-agent designs, MCP servers, replacing rule-based scoring with an LLM,
and cloud or Kubernetes deployment.
