# Smart PMO Agent

**Oren Salami | Technology Project Management + AI Tools**

An AI-powered PMO assistant for technology project teams. Analyzes Monday-style project data to deliver project health visibility, risk detection, sprint insights, OKR alignment analysis, and AI-powered Q&A for project managers.

---

## Project Overview

The **Smart PMO Agent** connects to Monday-style project data and answers the questions every PM needs answered:

- What is the current project status?
- Which tasks are blocking the sprint?
- Which OKRs are at risk?
- Who is overloaded on the team?
- What should I focus on this week?
- What should we discuss in the retrospective?

This is not a generic chatbot. It is a purpose-built PMO assistant grounded in real Agile, Scrum, Sprint Ops, OKR, and capacity management methodology.

---

## Monday Integration

**Current version uses realistic local Monday-style demo data.**

The architecture includes a clean adapter layer (`src/integrations/`) that decouples the data source from the analysis engine. Switching from demo data to a live Monday workspace requires only one configuration change:

```
PMO_DATA_SOURCE=monday_api
```

No other code changes are required. See `docs/architecture.md` for the full design.

> This project currently uses realistic Monday-style mock data instead of a live Monday account.
> The architecture is intentionally prepared for future Monday API integration through an adapter/client layer.
> This keeps the portfolio project lightweight while still demonstrating real PMO integration thinking.

---

## Five Core Flows

| Flow | Input | Output |
|------|-------|--------|
| **Project Visibility** | Tasks, sprints, statuses, due dates | Health score, blockers, sprint progress |
| **Risk Detection** | Blocked tasks, OKR gaps, capacity signals | Risk registry with severities and mitigations |
| **Sprint Insights** | Sprint tasks, velocity, team distribution | Sprint health, retro talking points, bottlenecks |
| **OKR Alignment** | Tasks with OKR links, OKR registry | At-risk objectives, unaligned work percentage |
| **AI PMO Q&A** | Natural language question + project context | Contextual PM answer with methodology grounding |

---

## Architecture

```
data/monday_demo/*.json
        ↓
src/integrations/monday_mock_client.py  ← Active (adapter pattern)
src/integrations/monday_api_client.py   ← Future skeleton
        ↓
src/pmo/  src/risk/  src/okr/  src/reporting/
        ↓
src/pipeline/pmo_pipeline.py  ←  RAG + AI Q&A layer
        ↓
app/streamlit_app.py  ← 7-tab PMO dashboard
```

---

## How to Run

**Clone and install:**
```bash
git clone https://github.com/Oren1984/smart-pmo-agent.git
cd smart-pmo-agent
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
```

**Run the Streamlit UI:**
```bash
streamlit run app/streamlit_app.py
```

Open: http://localhost:8501

No API key, Monday account, or external service is required.

**Run with Docker:**
```bash
docker compose up --build
```

Open: http://localhost:8511

---

## Streamlit UI Tabs

| Tab | Contents | Export |
|-----|---------|--------|
| Executive Dashboard | Health score, status distribution, sprint progress, OKR summary, blockers | Health Report (.md) |
| Sprint Health | Velocity, task breakdown, team load, retro talking points | Sprint Summary (.csv) |
| Risks & Blockers | Risk registry by severity, blocked task detail table | Risk Registry (.csv) |
| OKR Alignment | Per-OKR KR progress, contributing tasks, unaligned work | — |
| Capacity / Workload | Per-owner task and point distribution, overload detection | — |
| AI PMO Assistant | Natural language Q&A — demo mode (no key) or OpenAI | — |
| About | Project explanation, architecture, demo guide | — |

---

## AI PMO Assistant

The AI assistant works in two modes:

| Mode | When | Quality |
|------|------|---------|
| **Demo mode** (default) | No OpenAI key — fully offline | Smart rule-based answers from live project data |
| **AI mode** | `OPENAI_API_KEY` set in `.env` | Full AI answers grounded in methodology docs + project data |

Both modes answer questions about project status, blockers, OKRs, capacity, sprint health, and retrospective preparation.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Integration | Adapter pattern (mock / Monday API) |
| PMO Analysis | Python (custom engine) |
| AI Q&A | RAG — ChromaDB + OpenAI / rule-based |
| Embeddings | Mock (default) · HuggingFace · OpenAI |
| Vector Store | ChromaDB |
| Config | Pydantic Settings + python-dotenv |
| Packaging | Docker + Docker Compose |
| Language | Python 3.11 |

---

## Demo Data

The project ships with a realistic Monday-style demo dataset for a fictional company **TechCo** building a SaaS product **FlowHQ**:

| Entity | Count | Details |
|--------|-------|---------|
| Boards | 2 | Product Development, Platform & Infrastructure |
| Tasks | 40 | Across 4 sprints + backlog, 8 team members, 4 OKRs |
| Sprints | 4 | Sprints 5–8 (1 active, 2 completed, 1 planned) |
| OKRs | 4 | Onboarding (At Risk), Churn (Off Track), Infrastructure (On Track), Team Health (On Track) |
| Risks | 8 | 1 Critical, 3 High, 3 Medium, 1 Low |
| Team | 8 | Yael M., Dan K., Oren S., Maya R., Lior H., Tali G., Ron A., Noa T. |

All data is local, fictional, and requires no account or internet connection.

---

## Export Reports

Three export options are available directly from the Streamlit dashboard:

| Export | Tab | Format |
|--------|-----|--------|
| Project Health Report | Executive Dashboard | Markdown (.md) |
| Sprint Summary | Sprint Health | CSV (.csv) |
| Risk Registry | Risks & Blockers | CSV (.csv) |

All exports are local — no data leaves your machine.

---

## Running Tests

```bash
pytest                          # full suite (59 tests)
pytest tests/unit/              # unit tests only
pytest tests/integration/       # integration tests
pytest tests/e2e/               # end-to-end flow
pytest --cov=src                # with coverage
```

All tests run in mock mode — no API key or Monday account required.

---

## Static Portfolio Site

```bash
cd static-site
python -m http.server 8000
```

Open: http://localhost:8000

---

## Documentation

| Document | Contents |
|----------|---------|
| `docs/architecture.md` | System design and data flow |
| `docs/project_plan.md` | Goals, scope, implementation phases |
| `docs/methodology_alignment.md` | Agile, Scrum, OKR, sprint ops mapping |
| `docs/demo_flow.md` | How to demo and present the project |
| `docs/testing_strategy.md` | Testing approach and coverage |
| `docs/known_limitations.md` | What is demo data, what is not, what is next |
| `docs/API_KEYS_GUIDE.md` | Setup guide for all configuration options |

---

## Project Category

**Technology Project Management + AI Tools**

This project demonstrates practical AI application for project management — not pure AI/ML engineering. It shows how to build a PMO assistant that helps a PM improve project visibility, detect risks earlier, align work to business goals, and answer natural language questions about project status.

---

## License

MIT License. See the LICENSE file for details.
