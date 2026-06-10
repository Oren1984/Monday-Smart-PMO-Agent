# Methodology Alignment — Smart PMO Agent

## Overview

The Smart PMO Agent is built around recognized project management methodologies. Each feature maps to a specific PM practice.

---

## Agile & Scrum

| PMO Agent Feature | Agile/Scrum Concept |
|------------------|---------------------|
| Sprint Health tab | Sprint velocity tracking and burndown analysis |
| Task status breakdown (Done / In Progress / Stuck / Blocked) | Sprint board visualization |
| Retrospective talking points | Sprint Retrospective facilitation |
| Blocker detection and escalation | Impediment removal (Scrum Master responsibility) |
| Sprint goal display | Sprint Goal definition (Scrum) |
| Previous sprint comparison | Historical velocity trend |

---

## Sprint Planning & Operations

| PMO Agent Feature | Sprint Planning Concept |
|------------------|------------------------|
| Velocity computation (completed / planned points) | Sprint velocity and capacity utilization |
| Carryover risk task count | Sprint carryover prediction |
| Overloaded owner detection | Capacity planning and load balancing |
| Sprint re-scope recommendation in risk mitigations | Mid-sprint scope management |
| Sprint goal visibility | Sprint commitment tracking |

---

## OKR Framework

| PMO Agent Feature | OKR Concept |
|------------------|-------------|
| OKR Alignment tab | OKR tracking and review |
| Key Result progress bars | KR measurement and grading |
| Task-to-OKR mapping (`okr_link` field) | Strategic alignment of sprint work |
| Unaligned work percentage | "OKR orphan" detection |
| At-risk OKR flagging | Quarterly OKR health review |
| OKR in risk registry | OKR-driven risk escalation |

---

## Risk Management

| PMO Agent Feature | Risk Management Concept |
|------------------|------------------------|
| Risk registry with severity levels (Critical / High / Medium / Low) | Risk identification and prioritization |
| Probability and Impact fields | Risk scoring matrix |
| Mitigation plans per risk | Risk response planning |
| Affected OKR field on risks | Risk-to-strategy mapping |
| Auto-derived capacity risks | Proactive risk detection |

---

## Capacity Management

| PMO Agent Feature | Capacity Concept |
|------------------|-----------------|
| Capacity tab — per-owner task and point distribution | Workload visualization |
| Overloaded owner detection (>= 5 active tasks) | Over-capacity alert |
| Blocked task count per owner | Trapped capacity detection |
| Bottleneck owner detection in sprint analysis | Single point of failure identification |
| Suggested redistribution in risk mitigations | Load balancing recommendations |

---

## PMO Visibility

| PMO Agent Feature | PMO Practice |
|------------------|-------------|
| Executive Dashboard — single-page health view | PMO executive reporting |
| Health score (Green / Yellow / Red) | RAG status reporting |
| Cross-board task visibility | Portfolio-level PMO oversight |
| Dependency tracking in task data | Cross-team dependency management |
| AI Q&A for PM questions | PMO advisory function |

---

## PM Methodology Knowledge Base

The AI assistant's knowledge base covers:

| Document | Methodology Coverage |
|----------|---------------------|
| `agile_scrum.md` | Scrum roles, ceremonies, artifacts, blockers, PMO+Agile integration |
| `sprint_planning.md` | Capacity calculation, dependency mapping, Sprint Goal, backlog selection |
| `retrospectives.md` | Retro formats, action tracking, anti-patterns, PM role |
| `okr_alignment.md` | OKR structure, grading, cascade from strategy to sprint, common mistakes |
| `capacity_management.md` | Focus factor, workload distribution, bus factor, overload patterns |
