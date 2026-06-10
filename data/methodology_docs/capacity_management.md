# Capacity Management

## What is Capacity Management?

Capacity management in project management is the process of ensuring the team has enough available time, skills, and resources to deliver the planned work — without burning out or dropping quality.

Poor capacity management is one of the most common causes of sprint failure, missed deadlines, and team attrition.

## Why Capacity Management Matters

- **Over-capacity**: Team is committed to more work than they can deliver → missed commitments, stress, quality drops
- **Under-capacity**: Team has spare bandwidth → missed opportunities to deliver business value
- **Imbalanced capacity**: One team member carries disproportionate load → single point of failure and burnout risk

## Calculating Team Capacity

### Per-person available points

```
Available hours = Working days × Daily hours × Focus factor
Story points capacity = Available hours ÷ Hours per story point
```

Example:
- 10 working days × 8 hours/day = 80 hours
- Focus factor 0.75 (meetings, reviews, etc.) = 60 effective hours
- Average story point = 4 hours → capacity = 15 story points

### Team capacity
Sum each team member's individual capacity. Avoid treating the team as a single pool — individual skills matter.

## Focus Factor

The focus factor accounts for time not spent directly on sprint work:
- Daily standups: ~15 min/day
- Sprint ceremonies: 4–8 hours per sprint
- Code reviews: ~1 hour/day for most developers
- Slack and email: ~30 min/day
- Ad hoc support and meetings: varies

A healthy focus factor is **0.65–0.80**. Below 0.65 suggests too many meetings or context-switching. Above 0.85 suggests the team is not accounting for overhead.

## Workload Distribution

Signs of unhealthy workload distribution:

| Pattern | Risk | Action |
|---------|------|--------|
| One person owns > 40% of sprint points | Single point of failure | Redistribute or pair-program |
| Owner with 3+ blocked or stuck tasks | Capacity trapped in unresolvable work | Escalate blockers immediately |
| Owner with 0 tasks | Underutilized / misaligned | Assign supporting tasks or OKR work |
| All critical tasks owned by one person | Bus factor = 1 | Knowledge sharing, pairing |

## Bus Factor

The bus factor (or truck factor) measures how many people can leave the team before critical knowledge is lost. A bus factor of 1 means one person leaving halts delivery.

Healthy teams:
- Have at least 2 people familiar with each critical system area
- Document architecture and runbooks
- Cross-train through pairing and code reviews
- Rotate ownership of high-risk tasks across sprints

## Capacity Planning for Sprints

Before each sprint:
1. Check team calendar for planned absences (vacation, training, conferences)
2. Verify on-call rotation — on-call weeks reduce sprint capacity by ~30%
3. Check for carryover from previous sprint — carryover consumes new sprint capacity
4. Identify new joiners — new team members contribute at 30–50% capacity for first 2 sprints

## Overload Warning Signs

A team member is showing signs of overload when:
- They own more tasks than others but their velocity is declining
- They are mentioned in multiple blocker comments
- They are on the critical path for 3+ other tasks
- They are consistently working after hours (visible from commit timestamps)
- They carry over work from sprint to sprint

## Capacity and Risk

Over-capacity creates compounding risk:
1. Team rushes → code quality drops
2. Quality drops → more bugs
3. More bugs → QA load increases
4. QA load increases → QA team becomes bottleneck
5. Bottleneck → blocked tasks → sprint fails

Protecting capacity is risk management, not slacking.

## Capacity Management Tools

| Tool | Purpose |
|------|---------|
| Sprint burndown chart | Track whether team is on pace to complete commitment |
| Capacity heat map | Visualize workload per person across sprints |
| Blocker age tracking | Flag how long tasks have been stuck |
| Velocity trend | Detect capacity degradation over time |

## PMO Role in Capacity Management

A PMO supports capacity management by:
- Maintaining a cross-team capacity overview
- Identifying capacity bottlenecks that block other teams
- Escalating single-point-of-failure risks to leadership
- Rebalancing work across teams when one team is overloaded
- Tracking capacity utilization trends across quarters
- Protecting team capacity from excessive stakeholder requests and scope creep
