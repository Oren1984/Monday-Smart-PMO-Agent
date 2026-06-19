# Architecture — Monday Smart PMO Agent

## System Overview

The Monday Smart PMO Agent is structured as four independent layers connected by typed data contracts.

```
┌─────────────────────────────────────────────────────────┐
│  DATA LAYER                                             │
│  MondayMockClient  ←→  MondayClientBase  ←→  MondayAPIClient (future)  │
│  data/monday_demo/*.json                                │
└──────────────────────────┬──────────────────────────────┘
                           │ PMO DTOs
┌──────────────────────────▼──────────────────────────────┐
│  PMO ANALYSIS ENGINE                                    │
│  project_health.py · sprint_analyzer.py                 │
│  risk_detector.py · okr_analyzer.py · capacity_tracker.py │
└──────────────────────────┬──────────────────────────────┘
                           │ Analysis results → report_builder.py → pmo_context dict
┌──────────────────────────▼──────────────────────────────┐
│  AI / RAG PIPELINE                                      │
│  pmo_pipeline.py                                        │
│  Methodology doc indexing → ChromaDB                    │
│  Semantic retrieval → OpenAI generation / mock answers  │
└──────────────────────────┬──────────────────────────────┘
                           │ PMOAnswer
┌──────────────────────────▼──────────────────────────────┐
│  STREAMLIT UI                                           │
│  7 tabs: Dashboard · Sprint · Risks · OKR · Capacity    │
│          AI Assistant · About                           │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 1 — Data Layer (src/integrations/)

The data layer uses an **adapter pattern** to decouple the data source from the rest of the system.

### MondayClientBase (src/core/contracts.py)

Abstract interface that all Monday clients must implement:
- `get_boards() -> List[PMOBoard]`
- `get_tasks(board_id, sprint) -> List[PMOTask]`
- `get_sprints() -> List[PMOSprint]`
- `get_risks() -> List[PMORisk]`
- `get_okrs() -> List[PMOOKR]`

### MondayMockClient (src/integrations/monday_mock_client.py)

**Active in v1.** Loads JSON files from `data/monday_demo/` and normalizes them into typed PMO DTOs. The rest of the system never reads raw JSON — only normalized DTOs.

### MondayAPIClient (src/integrations/monday_api_client.py)

**Skeleton placeholder in v1.** Raises `NotImplementedError`. Future implementation will use Monday's GraphQL API. No changes to any other layer are needed when this is implemented.

### Factory function (src/integrations/__init__.py)

`get_monday_client(data_source)` returns the correct client based on `PMO_DATA_SOURCE` env var.

---

## Layer 2 — PMO Analysis Engine (src/pmo/, src/risk/, src/okr/)

Pure analysis logic. No UI dependencies. Each module accepts typed PMO DTOs and returns typed result DTOs.

| Module | Input | Output |
|--------|-------|--------|
| `project_health.py` | `List[PMOTask]`, optional `PMOSprint` | `ProjectHealthReport` |
| `sprint_analyzer.py` | `PMOSprint`, `List[PMOTask]` | `SprintReport` |
| `capacity_tracker.py` | `List[PMOTask]` | `CapacityReport` |
| `risk_detector.py` | `List[PMORisk]`, optional analysis outputs | `List[PMORisk]` (sorted) |
| `okr_analyzer.py` | `List[PMOOKR]`, `List[PMOTask]` | `OKRAlignmentReport` |
| `report_builder.py` | All analysis outputs | `Dict` (pmo_context) |

### Health Scoring

```
Green  — < 15% tasks blocked/stuck  AND  sprint >= 55% complete
Yellow — 15–30% blocked/stuck       OR   sprint 35–54% complete
Red    — > 30% blocked/stuck        OR   sprint < 35% complete
```

### Sprint Health

```
Healthy        — velocity >= 75%
Needs Attention — velocity 50–74%
At Risk        — velocity < 50%
```

---

## Layer 3 — AI / RAG Pipeline (src/pipeline/pmo_pipeline.py)

Handles the AI Q&A feature independently of the PMO analysis engine.

### Methodology doc indexing

On startup, indexes all `.md` files in `data/methodology_docs/` into ChromaDB:
1. Load each file via `DocumentLoader`
2. Chunk via `RecursiveChunker`
3. Embed via the configured `EmbeddingProvider`
4. Store in `ChromaVectorStore`

### Query flow

1. Embed the question
2. Search ChromaDB for relevant methodology passages
3. Combine top-3 passages with the live `pmo_context` dict
4. Generate answer: OpenAI (if key configured) or smart rule-based (mock mode)

### Mock mode answers

When no OpenAI key is present, `_mock_answer()` uses keyword detection to route the question to one of 9 specialized response generators, each pulling real data from `pmo_context`. This makes the demo fully functional offline.

---

## Layer 4 — Streamlit UI (app/streamlit_app.py)

Single-file UI with 7 tabs. Business-oriented language throughout — no technical RAG terminology visible to users.

| Component | Behavior |
|-----------|---------|
| Data loading | `@st.cache_data` — loads once per session |
| Analysis | Runs on every sidebar interaction or refresh |
| AI pipeline | Lazy-initialized, methodology docs indexed once |
| Session state | All analysis results stored in `st.session_state` |

---

## Data Contracts (src/core/contracts.py)

All inter-layer communication uses typed Python dataclasses. The integration layer normalizes raw JSON into these DTOs. The PMO engine consumes them. The UI reads from analysis output DTOs.

Key DTOs: `PMOTask`, `PMOSprint`, `PMORisk`, `PMOOKR`, `PMOKeyResult`, `PMOBoard`,
`ProjectHealthReport`, `SprintReport`, `CapacityReport`, `OKRAlignmentReport`, `PMOAnswer`

---

## Configuration (src/core/config.py)

All settings loaded from `.env` via Pydantic Settings. Key settings:

| Setting | Default | Purpose |
|---------|---------|---------|
| `PMO_DATA_SOURCE` | `mock` | Which Monday client to use |
| `EMBEDDING_PROVIDER` | `mock` | Embedding provider for methodology indexing |
| `OPENAI_API_KEY` | empty | Enables full AI Q&A mode |
| `MONDAY_API_TOKEN` | empty | Future: live Monday integration |
