# Example Evaluation Scenarios — Monday Smart PMO Agent

These scenarios describe realistic PMO situations and the expected agent behavior for each. Use them for demos, testing, and evaluation.

---

## Scenario 1 — Sprint Overload Detected

**Context:**
A sprint has too many high-priority tasks assigned to the same person or team. One owner has 12 story points of blocked or stuck tasks in addition to 20+ open points in the same sprint.

**Input:**
- Sprint tasks for the active sprint
- Per-owner task distribution and story point totals
- Blocked and stuck task counts per owner

**Expected Agent Output:**
- Flags the affected owner as overloaded
- Highlights the sprint as "At Risk" or "Needs Attention"
- Surfaces the overloaded owner in the Capacity tab with visual overload indicator
- Lists blocked/stuck tasks contributing to the overload signal
- Recommends human PM review to reassign or descope tasks

**Human Action Required:**
The PM reviews the flagged overload and decides whether to reassign tasks, reduce scope, or accept the risk for this sprint.

---

## Scenario 2 — OKR Alignment Gap

**Context:**
Several active sprint tasks are not linked to any OKR. The team is busy but the PMO cannot confirm that the work is contributing to strategic objectives.

**Input:**
- Active sprint task list with `okr_link` fields
- OKR registry with objectives and key results

**Expected Agent Output:**
- Calculates unaligned work percentage (tasks with no OKR link as % of total active tasks)
- Flags OKRs with low or no contributing tasks
- Surfaces the alignment gap in the OKR Alignment tab
- Suggests mapping unlinked tasks to relevant objectives for human review
- Highlights which OKRs are at risk due to insufficient task support

**Human Action Required:**
The PM or PMO lead reviews unlinked tasks and maps them to OKRs, or makes a deliberate decision to classify them as operational work outside OKR scope.

---

## Scenario 3 — Delivery Risk Detected

**Context:**
A key task is delayed past its due date and is blocking two other tasks in the sprint. The affected tasks are linked to a high-priority OKR.

**Input:**
- Task data with `due_date`, `status` (Blocked/Stuck), and `dependencies`
- Risk registry (or inferred risk signal from task data)
- OKR link on the blocking task

**Expected Agent Output:**
- Flags the blocking task as a delivery risk
- Shows the downstream impact (blocked dependent tasks, affected OKR)
- Surfaces the risk in the Risks & Blockers tab with severity (High or Critical)
- Explains the impact chain: delayed task → blocked tasks → at-risk OKR
- Recommends escalation for human PM/PMO review
- Provides mitigation options (unblock, reassign, descope, escalate)

**Human Action Required:**
The PM reviews the risk, decides on escalation, coordinates with the task owner to resolve the blocker, and updates the sprint plan accordingly.

---

## Scenario 4 — Executive PMO Summary

**Context:**
The PMO lead needs a concise portfolio-level summary before a leadership review. The portfolio contains one active sprint, multiple OKRs in various states, team workload data, and an open risk registry.

**Input:**
- Portfolio health report (Green/Yellow/Red health score)
- Active sprint status (velocity, task breakdown)
- Risk registry (severity distribution)
- OKR alignment report (on-track, at-risk, off-track counts)
- Team capacity report (overloaded members, blocked task counts)

**Expected Agent Output:**
- Generates a concise executive PMO summary covering:
  - Portfolio health status (overall score and key signals)
  - Active sprint progress (velocity, completion %, key blockers)
  - Top risks (Critical and High severity with brief mitigation notes)
  - OKR status (how many On Track / At Risk / Off Track)
  - Team capacity summary (overloaded members, capacity concerns)
  - Recommended follow-up actions for the PM/PMO to review
- Available as a Markdown export from the Executive Dashboard tab

**Human Action Required:**
The PMO lead reviews the summary, validates it against context they hold outside the data (verbal updates, informal agreements), adds any manual commentary, and presents to leadership with their own judgment applied.

---

## Scenario 5 — Retrospective Preparation

**Context:**
The sprint is ending and the Scrum Master or PM needs talking points for the retrospective.

**Input:**
- Completed sprint task data
- Sprint velocity (planned vs. completed points)
- Blocked and stuck task history
- Team load distribution during the sprint

**Expected Agent Output:**
- Auto-generates retrospective talking points covering:
  - Sprint velocity vs. target
  - Blocked tasks that slowed the team
  - Overloaded or underloaded team members
  - OKR progress achieved vs. expected
  - Carryover risk (tasks not completed that move to next sprint)
- Surfaces these in the Sprint Health tab under "Retrospective Talking Points"

**Human Action Required:**
The Scrum Master or PM uses these as a starting point for the retro conversation. They add qualitative observations, team dynamics context, and facilitation judgment that the agent cannot provide.

---

## How to Use These Scenarios in a Demo

1. Open the Streamlit app: `streamlit run app/streamlit_app.py`
2. The demo data is pre-configured to surface signals for Scenarios 1–5 simultaneously
3. Walk through each tab to demonstrate the relevant scenario:
   - **Executive Dashboard** → Scenario 4 (Executive Summary)
   - **Sprint Health** → Scenario 1 (Overload), Scenario 5 (Retro Points)
   - **Risks & Blockers** → Scenario 3 (Delivery Risk)
   - **OKR Alignment** → Scenario 2 (Alignment Gap)
   - **Capacity / Workload** → Scenario 1 (Overload detail)
   - **AI PMO Assistant** → Ask natural language questions about any scenario

See `docs/demo_flow.md` for the full step-by-step demo script.
