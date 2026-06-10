# Sprint Planning

## Purpose

Sprint Planning is the ceremony that kicks off every sprint. The team answers two questions:
1. **What can be done this sprint?** — Select items from the backlog
2. **How will the chosen work get done?** — Break items into tasks and estimate effort

A well-run sprint planning session produces a clear Sprint Goal and a committed Sprint Backlog.

## Sprint Goal

The Sprint Goal is a single objective that gives the sprint cohesion and direction. It explains *why* the team is doing this work, not just *what* they are doing.

Good Sprint Goal: "Ship the user onboarding redesign and unblock the retention data pipeline so we can begin NPS tracking."

Bad Sprint Goal: "Complete t001, t002, t004, t006, t007."

The Sprint Goal should:
- Be achievable within the sprint
- Align with one or more OKRs
- Be understandable by non-technical stakeholders
- Give the team flexibility in how they reach it

## Capacity Planning

Before selecting backlog items, the team must calculate sprint capacity.

### Calculating Capacity

1. Count available working days per team member
2. Subtract planned absence (vacation, training, on-call rotation)
3. Apply a focus factor (typically 70–80% to account for meetings, reviews, support)

Example:
- Team of 5 engineers × 10 working days × 7 productive hours/day × 0.75 focus factor = 262 person-hours
- If average story point = 4 hours, capacity ≈ 65 story points

### Capacity Warning Signs
- Sprint backlog consistently exceeds capacity → team is over-committing
- Velocity declining over 2+ sprints → systemic blocker or team burnout
- One person owns > 40% of sprint points → single point of failure

## Backlog Prioritization

The Product Owner brings a prioritized backlog to planning. Prioritization criteria:

| Method | Description |
|--------|-------------|
| MoSCoW | Must-have, Should-have, Could-have, Won't-have |
| WSJF | Weighted Shortest Job First — value ÷ effort |
| Risk-adjusted priority | High risk items pulled earlier |
| OKR alignment | Items directly contributing to OKRs get priority |

## Sprint Backlog Selection

The team selects items from the top of the prioritized backlog until capacity is filled.

Rules:
- Never pull items that are not "sprint ready" (no unclear requirements, missing designs, or unresolved dependencies)
- Flag dependencies before the sprint starts
- Identify the critical path — which items block other items?
- Leave 10–15% buffer for unplanned work and bug fixes

## Managing Dependencies

Dependencies are the most common cause of sprint failure. Before the sprint starts:

1. Map all inter-task dependencies (which task requires another to be done first?)
2. Map all cross-team dependencies (which tasks require something from another team?)
3. Flag external dependencies (vendor, design, security approval, etc.)
4. Escalate any dependency that cannot be resolved before the sprint starts

## Sprint Commitment vs. Stretch Goals

A sprint commitment is work the team is confident they can complete. A stretch goal is additional work that the team will attempt if the commitment is met early.

The sprint commitment should be protected. Stretch goals are optional.

## Re-Scoping a Sprint

Mid-sprint scope changes should be avoided. If they are unavoidable:
1. Bring the change to the Scrum Master and Product Owner
2. Remove equivalent points from the sprint backlog before adding new work
3. Update the Sprint Goal if the change materially shifts the sprint objective
4. Document the change and reason in the sprint record

## Sprint Health Indicators

| Indicator | Healthy Signal | Warning Signal |
|-----------|---------------|----------------|
| Velocity | Consistent with last 3 sprints | Drop > 20% from average |
| Blockers | Zero or resolved within 24h | Blockers older than 48h |
| Task completion | Linear burn-down | Front-loaded or flat burn-down |
| Carryover | < 10% of points | > 20% of points |
| Scope change | Zero mid-sprint | Multiple unplanned additions |

## Sprint Planning Common Mistakes

1. **Over-committing** — taking more points than capacity allows
2. **Skipping dependency mapping** — discovering blockers mid-sprint
3. **Unclear Sprint Goal** — team is pulling in different directions
4. **No buffer** — zero slack for bug fixes or urgent support requests
5. **Not reviewing previous sprint** — repeating the same process problems
