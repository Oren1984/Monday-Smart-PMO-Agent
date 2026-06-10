# OKR Framework — Objectives and Key Results

## What are OKRs?

OKRs (Objectives and Key Results) are a goal-setting framework that connects company strategy to team execution. They were popularized at Intel by Andy Grove and adopted widely by Google and tech companies globally.

**Objective**: A qualitative, inspirational statement of what you want to achieve.
**Key Results**: 2–5 measurable outcomes that prove the Objective is being met.

## OKR Structure

```
Objective: Improve User Onboarding
  KR1: Reduce time-to-first-value from 7 days to 2 days
  KR2: Achieve 40% Day-30 activation rate
  KR3: Ship onboarding redesign by end of quarter
```

## Good vs. Bad OKRs

### Good Objective
- Inspiring and directional
- Achievable within the OKR period (usually a quarter)
- Clear to everyone without explanation
- Qualitative — describes a desired state, not a number

### Bad Objective
- "Increase revenue by 20%" — this is a KR, not an O
- "Build the analytics dashboard" — this is a task, not an objective
- "Do better" — too vague

### Good Key Result
- Measurable — has a clear metric and target
- Outcome-oriented — measures impact, not output
- Time-bound — achievable within the OKR period
- Binary or continuous — either done/not-done, or a scale

### Bad Key Result
- "Improve performance" — not measurable
- "Ship 5 features" — output, not outcome
- "Hold 10 meetings" — activity, not result

## OKR Grading

OKRs are typically graded on a 0.0 – 1.0 scale at the end of the period:
- 0.7 – 1.0: Excellent
- 0.5 – 0.69: Good progress (acceptable if stretch goals were set)
- 0.3 – 0.49: Needs attention — root cause analysis required
- 0.0 – 0.29: Missed — major review needed

The "sweet spot" is 0.6–0.7. If you consistently score 1.0, your OKRs are not ambitious enough.

## OKR Alignment — Strategic to Team Level

OKRs cascade from company to department to team:

```
Company OKR: Become the leading project management tool for tech teams
  ↓
Product OKR: Improve User Onboarding
  ↓
Frontend Team OKR: Ship onboarding redesign and reduce UX friction
  ↓
Sprint Goal: Complete onboarding flow v2 and checklist component
  ↓
Sprint Tasks: t001, t006, t013...
```

Each sprint task should be traceable to an OKR. Work that does not contribute to any OKR is "unaligned work" — it may be necessary (bug fixes, maintenance) but should be explicitly acknowledged and limited.

## Task-to-OKR Mapping

A PMO should regularly review task-to-OKR alignment:

1. **Aligned work**: Tasks with a clear `okr_link` that match an active KR
2. **Supporting work**: Infrastructure or process tasks that enable OKR achievement (not directly measured)
3. **Unaligned work**: Tasks with no OKR connection — should be explained or re-prioritized
4. **OKR orphans**: OKRs with few or no tasks contributing to them — these KRs will be missed

## OKR Health Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| KR progress < 30% at mid-quarter | At serious risk | Escalate, re-scope, or adjust target |
| OKR has 0 contributing tasks in current sprint | Neglected | Pull aligned work into next sprint |
| Same KR missed 2 quarters in a row | Target is wrong or blocker is systemic | Revisit the target and root cause |
| > 25% of sprint tasks unaligned | Team working on wrong things | Backlog reprioritization session |

## OKRs and Sprint Planning

Before sprint planning, the PM or Product Owner should:
1. Review OKR progress — which KRs need the most work?
2. Ensure sprint backlog contains enough OKR-aligned tasks
3. Flag OKRs at risk and prioritize their contributing tasks
4. Avoid over-indexing on "unaligned" technical debt work

## OKRs vs. KPIs

| OKRs | KPIs |
|------|------|
| Strategic goal-setting | Operational performance monitoring |
| Set quarterly | Tracked continuously |
| Change each quarter | Stable over time |
| Ambitious by design | Expected to hit consistently |
| Drive change and improvement | Maintain and measure ongoing health |

Both are needed. KPIs tell you if the engine is running. OKRs tell you if you are driving in the right direction.

## Common OKR Mistakes

1. **Too many OKRs** — more than 3–5 OKRs per team creates confusion
2. **OKRs as task lists** — Key Results should be outcomes, not activities
3. **No ownership** — every OKR needs a clear owner
4. **Set and forget** — OKRs need weekly or bi-weekly check-ins to be useful
5. **Punishing misses** — low OKR scores should trigger learning, not blame
