# Setup Guide — Monday Smart PMO Agent

## Default Mode: No API Keys Required

The Smart PMO Agent runs fully offline by default. Copy `.env.example` to `.env` and run — no Monday account, Monday API token, workspace ID, or any other credential is needed. Setting `MONDAY_API_TOKEN` or `MONDAY_WORKSPACE_ID` today does not activate live Monday integration — `MondayAPIClient` remains an intentionally unimplemented placeholder (see `docs/GOVERNANCE_SECURITY_OBSERVABILITY.md`).

```bash
cp .env.example .env
streamlit run app/streamlit_app.py
```

---

## Optional: OpenAI (for full AI Q&A)

Adding an OpenAI key enables AI-generated PMO answers instead of the rule-based demo mode.

1. Get a key from: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```
3. Optionally switch embedding provider:
   ```
   EMBEDDING_PROVIDER=openai
   EMBEDDING_MODEL=text-embedding-3-small
   ```

**Cost:** The AI assistant uses `gpt-4o-mini`. A typical demo session costs less than $0.01.
Once enabled, each AI answer in the UI also shows a lightweight, advisory cost-awareness
note (a rough per-query estimate, not billing data) so a PM has a budget expectation
before relying on the OpenAI path — see `docs/GOVERNANCE_SECURITY_OBSERVABILITY.md`
Section 9.

---

## Optional: HuggingFace (free semantic embeddings)

For better methodology doc retrieval without any API key:
```
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Downloads a ~90MB model on first use. No API key required.

---

## Optional: Gemini

```
GEMINI_API_KEY=<your-key>
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=models/text-embedding-004
```

---

## Future: Monday API (not available in v1)

When Monday API integration is implemented:
```
PMO_DATA_SOURCE=monday_api
MONDAY_API_TOKEN=<your-token>
MONDAY_WORKSPACE_ID=<your-workspace-id>
```

No changes to any other part of the system are required. Setting these values
today has no effect — `PMO_DATA_SOURCE=monday_api` currently raises
`NotImplementedError` by design.
