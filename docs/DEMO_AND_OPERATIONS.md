# Demo and Operations

How to install, start, configure, and demonstrate the app, plus fixes for common problems.
By default everything runs offline on fictional demo data, with no account or API key.

---

## Installation

Requirements: Python 3.11 or later and Git. Docker is optional.

```bash
git clone https://github.com/Oren1984/Monday-Smart-PMO-Agent.git
cd Monday-Smart-PMO-Agent
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
cp .env.example .env            # Windows CMD: copy .env.example .env
```

`requirements.txt` includes optional packages (sentence-transformers, openai,
google-generativeai), so the first install can take a while.

## Starting Locally

```bash
streamlit run app/streamlit_app.py
```

Open http://localhost:8501. The sidebar should read **"Using local Monday-style demo data"**.

## Starting with Docker

```bash
cp .env.example .env            # required: docker-compose.yml loads .env
docker compose up --build
```

Open http://localhost:8511. The container listens on 8501, which Compose maps to 8511 on
the host. It runs as a non-root user and mounts `data/`, `vector_db/`, and `results/`
from the project folder.

## Configuration

Settings are read from environment variables or `.env` (`src/core/config.py`). The
defaults run the full demo.

| Variable | Default | Effect |
|----------|---------|--------|
| `PMO_DATA_SOURCE` | `mock` | `mock` loads demo data. `monday_api` is a placeholder and stops the app with an error. |
| `OPENAI_API_KEY` | empty | When set, the Q&A assistant answers with OpenAI `gpt-4o-mini` |
| `EMBEDDING_PROVIDER` | `mock` | `mock`, `huggingface`, or `openai` (needs `OPENAI_API_KEY`). Any other value, including `gemini`, falls back to `mock`. |
| `EMBEDDING_MODEL` | `mock-384` | Model name passed to the embedding provider. Set it explicitly when changing provider, for example `sentence-transformers/all-MiniLM-L6-v2` or `text-embedding-3-small`. |
| `MONDAY_API_TOKEN`, `MONDAY_WORKSPACE_ID` | empty | Reserved for a future Monday client; no effect today |
| `GEMINI_API_KEY` | empty | Not used by the app |

Cost: in default mode no external service is called, so there is no API cost. With
OpenAI enabled, each answer shows a rough estimate (about $0.002 per question). This is a
fixed advisory figure, not billing data.

Never put real keys in `.env.example` or any tracked file. `.env` is excluded from Git
and from the Docker build context.

## Demo Scenarios

Each scenario uses the bundled data (Sprint 7 active). Figures below were produced by the
current code. Overdue counts depend on today's date.

| # | Scenario | Where | What to point out |
|---|----------|-------|-------------------|
| 1 | Health at a glance | Executive Dashboard | **Yellow** health; Sprint 7 at 37% (22/60 points); 5 stuck or blocked tasks; OKR status cards; active blockers |
| 2 | Sprint behind plan | Sprint Health | **At Risk** sprint health; tasks by status; points per person; retrospective talking points; Sprint Summary CSV |
| 3 | Delivery risk | Risks & Blockers | Overall level **Critical**; OKR-2 risk with mitigation; blocked and stuck task table; Risk Registry CSV |
| 4 | Strategy gap | OKR Alignment | OKR-1 At Risk and OKR-2 Off Track, both with blocked contributing work; about 17% unaligned work |
| 5 | Team overload | Capacity | Dan K. and Lior H. flagged with 5+ active tasks; per-person blocked counts |
| 6 | Ask a question | AI PMO Assistant | Use the suggestion buttons, such as "What should I focus on this week?" The answer shows mode, sources, and cost note. |
| 7 | Summary export | Executive Dashboard | "Export Health Report" downloads a Markdown summary |

In each scenario, the reviewer decides what to do next. The app offers no action buttons
that change data.

Use the sidebar to view other sprints (5, 6, 8). **Refresh Analysis** reloads the same demo data.

## Images

### Application screenshots

Captured from the local app in default demo mode. All data shown is fictional.

![Executive Dashboard with Yellow health, Sprint 7 at 37% and At Risk, task status distribution, and OKR status](screenshots/03-app-executive-dashboard.png)
*Executive Dashboard: health score, sprint progress, task status, OKR status, and active blockers.*

![Risks and Blockers tab with an overall Critical risk level and the risk register sorted by severity](screenshots/04-app-risks-and-blockers.png)
*Risks & Blockers: severity counts and the risk register, with the critical OKR-2 risk expanded.*

### External-service screenshots

These show a Monday.com board used to plan and track the work of building this project.
The app does not read this board.

![Monday.com board with Sprint 1 and Sprint 2 groups of build tasks](screenshots/01-monday-project-board-sprints-overview.png)
*Monday.com: sprint groups for this project's own build tasks.*

![Monday.com backlog group with assistant and reporting tasks](screenshots/02-monday-project-board-ai-reports-backlog.png)
*Monday.com: backlog of assistant and reporting tasks.*

## Troubleshooting

| Problem | Cause and fix |
|---------|---------------|
| "Failed to load Monday demo data" | Usually `PMO_DATA_SOURCE=monday_api`, which is not implemented. Set it to `mock`. Also check that `data/monday_demo/` exists and that you started the app from the project root. |
| Port 8501 already in use | Run `streamlit run app/streamlit_app.py --server.port 8502`. |
| `docker compose` complains about `.env` | Create it first: `cp .env.example .env`. |
| "Methodology indexing skipped" warning | The Q&A layer could not index the methodology notes. Rule-based answers still work. Check `EMBEDDING_PROVIDER` and `EMBEDDING_MODEL`. |
| "Unable to generate answer. Please try again." | The OpenAI call failed. Check the key, network, and quota, or clear `OPENAI_API_KEY` to use rule-based answers. |
| HuggingFace embeddings slow on first start | The model is downloaded on first use. Later starts are faster. |
| Overdue count looks very high | Overdue is measured against today's date, and the demo due dates are in mid-2026. |
| Sources in answers seem unrelated | Mock embeddings are not semantic. Use `EMBEDDING_PROVIDER=huggingface` for meaningful retrieval. |
