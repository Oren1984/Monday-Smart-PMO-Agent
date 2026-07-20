# Static Site — Monday Smart PMO Agent

**Oren Salami | Technology Project Management + AI Tools**

---

## Overview

This folder contains a **standalone static portfolio page** for the Monday Smart PMO Agent project. It is built with plain HTML, CSS, and vanilla JavaScript — no framework, no build step, no dependencies.

This is not the Streamlit application. It is a visual presentation layer designed to introduce the project to technical reviewers, hiring managers, and PMO stakeholders.

---

## Purpose

The page presents the following aspects of the project:

- **Project overview** — what the PMO agent does and what problem it solves
- **Core flows** — Portfolio Visibility, Risk Monitoring, Sprint Insights, OKR Alignment, AI PMO Q&A
- **Architecture** — four-layer design from Monday data adapter to Streamlit UI
- **Human-in-the-Loop** — how the agent supports human judgment without replacing it
- **PM Methodology** — Agile, Scrum, OKR framework, capacity management grounding
- **Tech stack** — Streamlit, ChromaDB, Pydantic, OpenAI, Docker
- **Demo** — how to run locally and what the project demonstrates

---

## Folder Structure

```
static-site/
├── index.html      # Full landing page with all sections
├── styles.css      # Dark theme, glassmorphism cards, responsive grid, animations
├── app.js          # Sticky nav, active-section tracking, scroll reveal, smooth scroll
└── assets/         # Reserved for future static assets (currently unused)
```

---

## How to Run Locally

From the repository root:

```bash
cd static-site
python -m http.server 8000
```

Then open your browser at:

```
http://localhost:8000
```

No installation required. The site loads immediately from the local filesystem.

---

## What This Site Is

- A **standalone static portfolio page** for the Monday Smart PMO Agent
- A **visual presentation layer** — suitable for sharing with technical reviewers and PMO stakeholders
- Deployable to any **static hosting service** or plain web server by uploading the folder as-is
- **No build step required** — open `index.html` directly or serve it with any HTTP server

---

## What This Site Is Not

- **Not the Streamlit application** — run `streamlit run app/streamlit_app.py` for the interactive UI
- **Not the PMO analysis engine** — the analysis logic lives in `src/`
- **Not a backend service** — there is no server, no API, and no database behind this page
- **Not a real Monday integration** — the project uses demo data; live Monday API is a future extension

---

## Design Notes

The page uses a hand-crafted dark theme with no external CSS framework:

- **Dark navy base** (`#0a0e1a`) with indigo/cyan accent gradient
- **Glassmorphism cards** — `backdrop-filter: blur` with semi-transparent borders
- **Sticky navigation** with blur backdrop and active-section tracking
- **Responsive layout** using CSS Grid (`auto-fit / minmax`)
- **Scroll reveal animations** via `IntersectionObserver` (no scroll event listeners)
- **Vanilla JS only** — no jQuery, no React, no bundler

---

## Maintenance Notes

- **Update this site** when the core project changes significantly — for example, when a new capability or integration is added.
- **Do not mirror every small backend change** — minor refactors and test additions do not require a site update.
- **Keep claims aligned with the actual repository state.** If the site says the system supports a feature, that feature should exist in `src/` or `app/`.
