# Known Limitations — Smart PMO Agent

## Monday Integration

### Current version uses local demo data, not a live Monday account

This project currently uses realistic Monday-style mock data loaded from `data/monday_demo/*.json` instead of a live Monday workspace. The data represents a fictional company (TechCo) and is designed to be production-realistic but is not connected to any real project.

**The architecture is intentionally prepared for future Monday API integration through an adapter/client layer (`src/integrations/`).** Switching to real Monday data requires:
1. Obtaining a Monday personal access token
2. Setting `PMO_DATA_SOURCE=monday_api` and `MONDAY_API_TOKEN=<token>` in `.env`
3. Implementing the GraphQL queries in `monday_api_client.py`

No other code changes are needed.

### Demo dataset is fictional and static

The demo data covers 40 tasks, 4 sprints, 4 OKRs, 8 risks, and 8 team members for a fictional company (TechCo / FlowHQ). It is designed to surface all five PMO analysis flows with realistic complexity, but it is not connected to any real project or workspace.

### No real-time data sync

Because data is loaded from static JSON files, there is no real-time sync. Clicking "Refresh Analysis" in the sidebar reloads the same demo data. In a live Monday integration, this would fetch fresh board data.

---

## AI Q&A

### Mock mode responses are rule-based, not AI-generated

When no OpenAI key is configured, the AI assistant uses a keyword-matching rule system to generate answers from live project data. These answers are useful and data-grounded but are not AI-generated. Add `OPENAI_API_KEY` to `.env` for full AI responses.

### Mock embeddings do not capture semantic meaning

When `EMBEDDING_PROVIDER=mock`, methodology doc retrieval uses hash-based vectors that do not reflect semantic similarity. The AI Q&A still works (rule-based answers do not depend on semantic retrieval), but the methodology passages shown in "sources" may not be the most semantically relevant.

Use `EMBEDDING_PROVIDER=huggingface` for semantically meaningful retrieval without any API key.

---

## Export / Reporting

### Exports are local demo reports, not production reporting

The CSV and Markdown export features generate in-memory reports from the current analysis results. They are intended for portfolio demonstration and manual review — not as a production reporting pipeline.

- No reports are stored on disk by the application
- No email, no scheduler, no report history
- Markdown reports are styled for readability in a text editor or GitHub, not for enterprise report management systems

---

## System Design

### No real Monday account required

By design. This is a portfolio project demonstrating PMO integration thinking and AI application to project management. It runs fully offline.

### No multi-user authentication

The Streamlit app is a single-user local application. It is not designed for shared or public deployment. No login, session isolation, or role-based access is implemented.

### No persistent session storage

Analysis results are stored in Streamlit session state only. Closing the browser tab resets the session. Results are not persisted to disk between sessions.

### Demo data is fictional

All persons, companies, projects, and data in `data/monday_demo/` are fictional. Any resemblance to real projects or people is coincidental.

---

## Infrastructure

### Docker requires a running Docker daemon

`docker compose up --build` requires Docker Desktop (Windows/macOS) or the Docker daemon (Linux).

### No cloud deployment in v1

No Kubernetes, Helm, Terraform, or cloud provider configuration is included. The system is designed for local execution.

---

## Scope Boundaries

| Capability | Status |
|-----------|--------|
| Live Monday API integration | Future — adapter skeleton in place |
| Real-time data sync | Future — requires live API |
| Multi-user dashboard | Not planned for v1 |
| Notifications / alerts | Not planned for v1 |
| Gantt / timeline view | Not planned for v1 |
| Budget / cost tracking | Out of scope |
| Jira / Linear integration | Out of scope for v1 |
| Mobile responsive UI | Partially — Streamlit is responsive but not optimized for mobile |
