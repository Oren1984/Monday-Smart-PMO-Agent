# Demo Flow — Smart PMO Agent

## Purpose

This guide explains how to demonstrate the Smart PMO Agent in an interview or portfolio review.

---

## Before the Demo

1. Start the Streamlit app: `streamlit run app/streamlit_app.py`
2. Open: http://localhost:8501
3. Confirm the banner reads "Using local Monday-style demo data"
4. The data loads automatically — no setup needed

---

## Recommended Demo Order

### Step 1 — Executive Dashboard (2 min)

**What to show:**
- Point out the project health badge (Yellow or Red)
- Explain the 5 key metrics: total tasks, done, stuck/blocked, overdue, open risks
- Show the sprint progress bar and sprint health
- Point to the OKR status cards (At Risk / On Track)
- Highlight the Active Blockers section

**What to say:**
> "This is what a PM sees every morning — the full project health at a glance.
> The health score is computed from task statuses, sprint velocity, and blocker count.
> You can see Sprint 7 is only 35% complete with 4 blocked/stuck tasks — that's Yellow."

---

### Step 2 — Sprint Health (2 min)

**What to show:**
- Velocity gauge (35% — At Risk)
- Task breakdown expandable sections (show Stuck and Blocked)
- Team load bars — point out Lior H. (overloaded)
- Retrospective talking points

**What to say:**
> "The sprint analyzer computes velocity, detects bottlenecks, and generates
> retrospective talking points from the data automatically. Lior H. has 8 active tasks —
> the system flags this as a capacity risk."

---

### Step 3 — Risks & Blockers (1.5 min)

**What to show:**
- Overall Risk Level badge (Critical)
- Expand the Critical and High risk cards
- Show the mitigation suggestions
- Show the blocked task table at the bottom

**What to say:**
> "OKR-2 (Reduce Churn) is at critical risk because the churn detection API has been
> blocked for 3 days waiting for a schema approval. The system surfaces this, explains
> the impact on the OKR, and provides a concrete mitigation recommendation."

---

### Step 4 — OKR Alignment (2 min)

**What to show:**
- OKR-1 and OKR-2 expanded (At Risk)
- Key Result progress bars
- Contributing tasks section for OKR-1
- Unaligned work percentage

**What to say:**
> "The OKR analyzer maps each sprint task to its business objective using the `okr_link` field.
> You can see which key results are progressing, which are at risk, and how much sprint work
> has no OKR connection — that's your unaligned work percentage."

---

### Step 5 — AI PMO Assistant (3 min)

**What to show:**
- Click "Which OKRs are at risk?" suggestion button
- Click "What should I focus on this week?"
- Type a custom question: "What should we discuss in the retrospective?"
- Show that sources cite methodology docs

**What to say:**
> "The AI assistant combines two things: live analysis from the PMO engine — the same data
> powering the dashboard — and a knowledge base of PM methodology documents covering Agile,
> Scrum, sprint planning, OKRs, and capacity management. In demo mode it uses a smart
> rule-based engine. With an OpenAI key, it uses GPT-4o-mini for full AI-quality answers."

---

### Step 6 — Architecture Explanation (2 min, optional)

**What to explain:**
> "The key architectural decision is the Monday adapter pattern. The PMO analysis engine
> never reads raw JSON — it only consumes typed Python dataclasses from the Monday client.
> Right now `MondayMockClient` loads the local demo data. In the future, `MondayAPIClient`
> would call Monday's GraphQL API and return the exact same datatypes. One config change —
> `PMO_DATA_SOURCE=monday_api` — is all it takes."

---

## Step 6 — Export Feature (1 min)

**What to show:**
- In the Executive Dashboard, expand "📤 Export Health Report"
- Click "Download Health Report (.md)" — point out the download
- Open the file in any text editor to show the structured markdown

**What to say:**
> "The PM can export a Markdown health report at any time — a structured summary
> of project health, sprint status, risks, and OKR progress. It is a local file —
> no external service involved. The same pattern applies to the Sprint Summary CSV
> and Risk Registry CSV in their respective tabs."

---

## Common Interview Questions

**Q: Why not connect to the real Monday API?**
A: The architecture is designed for it. The `monday_api_client.py` skeleton is in place.
   A live connection would require a Monday account and a personal API token, which I
   excluded to keep the project self-contained and runnable by anyone without account setup.

**Q: How does the AI part work?**
A: Two layers. First, methodology docs (Agile, Scrum, OKR, etc.) are indexed into ChromaDB
   using embeddings. When a PM asks a question, semantically similar methodology passages
   are retrieved. Second, those passages are combined with live project analysis data and
   sent to OpenAI (or the rule-based mock) to generate a contextual PM answer.

**Q: Is the demo data realistic?**
A: It models a fictional SaaS company (TechCo) with a real-looking project: 8 team members,
   40 tasks, 4 OKRs, 8 risks, and a sprint that is behind schedule with realistic blockers.
   The data was designed to surface all five PMO analysis flows clearly.

**Q: What PM methodology does this use?**
A: Agile/Scrum for sprint management, OKR framework for business alignment, and standard
   capacity management principles for workload analysis. All are documented in `data/methodology_docs/`.
