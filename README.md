# ThreatView

An open-source **Threat Intelligence Platform (TIP)** for small and medium businesses.  
ThreatView aggregates Indicators of Compromise (IOCs) from public threat feeds, normalizes them into a unified schema, and surfaces them via a searchable React dashboard.

---

## Features

- 📡 **Live threat ingestion** — AlienVault OTX, PhishTank, URLhaus (abuse.ch), polled every 60 minutes
- 🔍 **IOC search** — full-text search across indicators, categories, countries, descriptions
- 📊 **Analytics** — severity breakdown, country heatmap, top malware families, ingestion trends
- 🗺️ **Threat Map** — geo-distributed threat origin visualization
- 🔔 **Alert Engine** — configurable rules (severity / keyword / IOC type / country) with dashboard + email notifications
- 🏷️ **Brand Monitoring** — domain impersonation detection across phishing feeds
- 📄 **PDF Reports** — downloadable weekly threat landscape report
- 📦 **Export** — bulk CSV / JSON download of the threat database
- 🐳 **Docker-ready** — single `docker-compose up` to run the full stack

---

## Quick Start

### Option A — Docker (recommended)

```bash
git clone https://github.com/your-org/threatview.git
cd ThreatView
cp backend/.env.example backend/.env
# Edit backend/.env — set SECRET_KEY and any feed API keys you have

docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:80 |
| Backend API | http://localhost:5000/api |
| API Docs | http://localhost:5000/api/docs |

### Option B — Manual (development)

**Backend**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env

flask --app run db upgrade
python run.py
# API running at http://localhost:5000
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL=http://localhost:5000/api
npm run dev
# UI running at http://localhost:5173
```

---

## Threat Feed Credentials

| Feed | Variable | Where to get it |
|---|---|---|
| AlienVault OTX | `OTX_API_KEY` | [otx.alienvault.com](https://otx.alienvault.com) → Profile → API keys |
| PhishTank | `PHISHTANK_APP_KEY` | [phishtank.com/developer_info.php](https://www.phishtank.com/developer_info.php) |
| URLhaus | `URLHAUS_AUTH_KEY` | [auth.abuse.ch](https://auth.abuse.ch) |

Missing keys cause a **graceful skip** — the other feeds continue unaffected.

---

## Project Structure

```
ThreatView/
├── backend/                   # Flask REST API
│   ├── app.py                 # Application factory
│   ├── run.py                 # Dev server / gunicorn entrypoint
│   ├── config.py              # Environment-driven config classes
│   ├── requirements.txt
│   ├── database/              # SQLAlchemy + Flask-Migrate instances
│   ├── models/                # Threat, Alert, BrandMonitor, User
│   ├── routes/                # Blueprints (threats, alerts, stats, search, export, report)
│   ├── services/              # Business logic layer
│   ├── ingestors/             # Per-feed ingestion modules
│   ├── scheduler/             # APScheduler wiring + job functions
│   ├── schemas/               # Marshmallow serialization
│   ├── utils/                 # Logging, RBAC, pagination, constants
│   └── migrations/            # Alembic migration scripts
│
├── frontend/                  # React 18 + Vite SPA
│   ├── src/
│   │   ├── pages/             # Dashboard, ThreatFeed, Analytics, Search, Settings
│   │   ├── components/        # Reusable UI components + charts
│   │   ├── hooks/             # Data-fetching hooks
│   │   ├── services/          # Axios API calls
│   │   ├── context/           # Sidebar + Preferences context
│   │   └── layouts/           # MainLayout wrapper
│   └── public/
│
├── docker-compose.yml
├── .gitignore
├── LICENSE
└── README.md
```

---

## API Reference

All routes prefixed with `/api`. Full interactive docs at `/api/docs` (Swagger UI).

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness + DB connectivity |
| GET | `/threats` | Paginated, filtered IOC listing |
| GET | `/threats/<id>` | Single threat detail |
| GET | `/stats` | Dashboard aggregate statistics |
| GET | `/stats/malware-trends` | Malware family trend data |
| GET | `/search?q=` | Full-text IOC search |
| GET/POST | `/alerts/rules` | Alert rule CRUD |
| GET | `/alerts/events` | Alert event inbox |
| GET/POST | `/alerts/brand-monitors` | Brand monitor CRUD |
| GET | `/export` | Bulk CSV/JSON download |
| GET | `/report/weekly` | PDF report download |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · Flask 3.0 · SQLAlchemy · APScheduler · Marshmallow · ReportLab |
| Database | PostgreSQL (production) · SQLite (development) |
| Frontend | React 18 · Vite 6 · Recharts · Bootstrap 5 · React Router 6 |
| Container | Docker · Docker Compose · Nginx |

---

## License

MIT — see [LICENSE](LICENSE).
