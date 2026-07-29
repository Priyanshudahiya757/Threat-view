# ThreatView Frontend

A React dashboard for the ThreatView threat intelligence platform. Consumes
the Flask backend's REST API directly — no mock data.

This repository is the **frontend only**. It expects the backend to already
be running (see the separate `backend/` project).

## Tech stack

React 18 · Vite · React Router DOM · Axios · Bootstrap 5 · React Icons ·
Recharts · React Toastify · PropTypes

## Project structure

```
frontend/
├── public/                 # favicon
├── src/
│   ├── assets/               # brand mark
│   ├── components/            # reusable UI (table, cards, badges, modal...)
│   │   └── charts/              # the 5 Recharts visualizations
│   ├── pages/                   # one file per route
│   ├── services/                  # axios instance + API functions
│   ├── hooks/                      # data-fetching hooks (one per endpoint)
│   ├── context/                     # sidebar + local display preferences
│   ├── layouts/                      # sidebar/navbar/footer shell
│   ├── styles/                        # design tokens + component styles
│   ├── App.jsx
│   └── main.jsx
├── index.html
├── package.json
└── vite.config.js
```

## Setup

```bash
cd frontend
npm install

cp .env.example .env
# edit .env if your backend isn't at http://localhost:5000/api

npm run dev          # http://localhost:5173
```

The dashboard will show connection-error states everywhere until the Flask
backend (from the companion `backend/` project) is running and reachable at
`VITE_API_URL` — there's no mock/offline mode, every screen is wired to a
real endpoint.

Production build:

```bash
npm run build     # outputs to dist/
npm run preview   # serve the production build locally
```

## Pages -> API mapping

| Page | Route | Backend calls |
|---|---|---|
| Dashboard | `/dashboard` | `GET /stats`, `GET /recent` |
| Threat Feed | `/threats` | `GET /threats` (paginated/filtered/sorted) |
| Threat Details | `/threats/:id` | `GET /threats/:id` |
| Search IOC | `/search` | `GET /search?q=` |
| Analytics | `/analytics` | `GET /stats`, `GET /threats` (100-row sample) |
| Settings | `/settings` | `GET /health` (polled every 30s) |

**Note on Analytics:** the backend's `/api/stats` endpoint returns severity,
country, and category breakdowns directly, but not "top sources" or a
time-series trend. Those two charts are derived client-side from the 100
most-recently-ingested threats (`useThreatAggregates` hook) rather than a
full-dataset aggregation — both charts are labeled accordingly in the UI. If
that sampling becomes a real limitation, the cleanest fix is adding
`top_sources` to `stats_service.py` on the backend the same way
`top_categories`/`top_countries` already work.

## Design system

Dark navy canvas (not pure black) with a four-color functional accent
system: blue and purple carry brand/chrome, red and amber carry severity
(amber was added beyond the brief's three named accents because a 4-tier
severity scale needs a distinct "caution" middle tone). Indicators, hashes,
and timestamps use a monospace face (JetBrains Mono) so analysts can compare
values character-by-character. Severity-coded left-edge accent bars are the
one recurring structural device, applied to stat cards and the activity
feed. All tokens live in `src/styles/global.css`.

## Known gaps / next steps

- No authentication — matches the backend, which is also unauthenticated in
  this phase.
- "Top Sources" and "Ingestion Trend" are sample-based (see note above).
- Settings preferences (page size, toast notifications) are stored in
  `localStorage` only; there's no backend endpoint for account-level
  settings yet.
