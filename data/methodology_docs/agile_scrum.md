# Agile and Scrum Framework

## What is Agile?

Agile is an iterative approach to project delivery that emphasizes collaboration, flexibility, and continuous improvement. Instead of delivering everything at the end of a long project, Agile teams deliver work in small, usable increments and adjust based on feedback.

Agile is guided by four core values from the Agile Manifesto:
1. Individuals and interactions over processes and tools
2. Working software over comprehensive documentation
3. Customer collaboration over contract negotiation
4. Responding to change over following a plan

## What is Scrum?

Scrum is the most widely used Agile framework. It organizes work into fixed-length iterations called sprints (typically 1–4 weeks). Each sprint produces a potentially shippable increment of the product.

### Scrum Roles

**Product Owner (PO)**
- Owns the product backlog
- Prioritizes work based on business value
- Represents stakeholders and customer needs
- Defines acceptance criteria for stories

**Scrum Master**
- Facilitates Scrum ceremonies
- Removes impediments (blockers) from the team
- Coaches the team on Agile practices
- Shields the team from outside distractions

**Development Team**
- Cross-functional group that does the actual work
- Self-organizes around sprint goals
- Responsible for sprint commitments
- Typically 3–9 people

### Scrum Ceremonies

**Sprint Planning**
- Held at the start of each sprint
- Team selects work from the backlog (sprint backlog)
- Defines a Sprint Goal
- Estimates work in story points or hours

**Daily Standup (Daily Scrum)**
- 15-minute daily sync
- Three questions: What did I do yesterday? What will I do today? Any blockers?
- Keeps the team aligned and exposes impediments early

**Sprint Review**
- Held at the end of the sprint
- Team demonstrates completed work to stakeholders
- Product Owner reviews and accepts or rejects work
- Updates the product backlog based on feedback

**Sprint Retrospective**
- Held after the sprint review
- Reflects on the process, not the product
- Three questions: What went well? What should improve? What actions will we take?
- Drives continuous improvement

**Backlog Refinement (Grooming)**
- Ongoing activity (not a formal Scrum ceremony)
- Team reviews upcoming backlog items
- Adds details, estimates, and acceptance criteria
- Ensures stories are "sprint ready"

### Scrum Artifacts

**Product Backlog**
- Ordered list of all work needed for the product
- Owned by the Product Owner
- Items are called user stories, epics, or tasks
- Continuously updated and reprioritized

**Sprint Backlog**
- Work selected for the current sprint
- Owned by the Development Team
- Should not change mid-sprint without a valid reason

**Increment**
- The sum of all completed sprint work plus all previous increments
- Must meet the Definition of Done
- Should be shippable at the end of every sprint

## Story Points and Velocity

**Story Points**
- Relative measure of effort, complexity, and uncertainty
- Common scales: Fibonacci (1, 2, 3, 5, 8, 13), T-shirt sizes (XS, S, M, L, XL)
- Not hours — they represent relative difficulty, not time

**Velocity**
- The average number of story points a team completes per sprint
- Used for forecasting and sprint planning
- A healthy, stable team will have consistent velocity within ±20%
- Declining velocity signals process problems or increasing complexity

## Blockers and Impediments

A blocker is anything preventing the team from completing planned work. Blockers should be:
1. Surfaced immediately (not hidden until standup)
2. Logged visibly on the board (e.g., status: Blocked)
3. Escalated if not resolved within 24 hours
4. Removed by the Scrum Master as a top priority

Common sources of blockers:
- Missing dependencies from another team
- Waiting for approvals or decisions
- Technical unknowns (spikes needed)
- External vendor delays
- Unclear requirements or acceptance criteria

## Definition of Done (DoD)

The Definition of Done is an agreed set of criteria that every completed work item must meet. A typical DoD includes:
- Code written and reviewed
- Unit tests passing
- Integration tests passing
- Deployed to staging environment
- Acceptance criteria verified by Product Owner
- Documentation updated

## Scrum and PMO Integration

A PMO (Project Management Office) can support Agile/Scrum teams by:
- Tracking sprint metrics across multiple teams
- Identifying systemic blockers and escalation patterns
- Aligning sprint work to strategic OKRs
- Reporting progress to executive stakeholders in business language
- Maintaining cross-team dependency maps
- Facilitating portfolio-level risk reviews
