# ThreatView Backend

An affordable Threat Intelligence Platform (TIP) backend for small and
medium businesses. ThreatView aggregates indicators of compromise (IOCs)
from public threat feeds, normalizes them into a single schema, stores
them in PostgreSQL, and exposes a searchable REST API for a future React
dashboard.

This repository is the **backend only**. No frontend is included.

## Tech stack

Python 3.12 · Flask · Flask-SQLAlchemy · Flask-Migrate · PostgreSQL ·
APScheduler · Requests · python-dotenv · Marshmallow · Gunicorn ·
Flask-CORS

## Project structure

```
backend/
├── app.py              # Flask application factory
├── config.py            # Environment-driven config classes
├── requirements.txt
├── .env.example
├── run.py                # Dev server entrypoint / gunicorn target
├── README.md
├── models/                # SQLAlchemy models (Threat, User)
├── routes/                # Blueprints (health, threats, stats, search)
├── services/              # Normalization, persistence, and stats logic
├── ingestors/             # One module per threat feed
├── scheduler/              # APScheduler wiring + job functions
├── database/                # db/migrate extension instances
├── schemas/                  # Marshmallow (de)serialization + validation
├── utils/                    # Logging, pagination, shared constants
└── logs/                      # Rotating log file lives here at runtime
```

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: at minimum set SECRET_KEY, DATABASE_URL, and the three
# feed credentials described below

# create the Postgres database referenced by DATABASE_URL, then:
flask --app run db init
flask --app run db migrate -m "initial schema"
flask --app run db upgrade

python run.py                      # http://localhost:5000
```

Production:

```bash
gunicorn run:app --bind 0.0.0.0:8000 --workers 4
```

### Threat feed credentials

| Feed | Auth | Notes |
|---|---|---|
| **AlienVault OTX** | `X-OTX-API-KEY` header | Free account at otx.alienvault.com (now operated under LevelBlue) -> profile -> API key. Set `OTX_API_KEY`. |
| **PhishTank** | keyed feed URL | Anonymous polling is rate limited. Register a free key at phishtank.com/developer_info.php and set `PHISHTANK_URL` to your personal keyed feed URL. |
| **URLhaus** (abuse.ch) | `Auth-Key` header | Free key at auth.abuse.ch — required on every request as of abuse.ch's platform-wide auth rollout. Set `URLHAUS_AUTH_KEY`. |

If a key is missing, that feed's ingestor logs the failure and returns
no results — it will never crash the other two scheduled jobs or the
API itself.

## API reference

All routes are prefixed with `/api`.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness + DB connectivity check |
| GET | `/threats` | Paginated, filterable, sortable threat listing |
| GET | `/threats/<id>` | Single threat by id |
| GET | `/stats` | Aggregate dashboard statistics |
| GET | `/search?q=` | Case-insensitive search across indicator/description/category/country |
| GET | `/recent` | Most recently ingested threats |

`GET /threats` query params: `page`, `per_page` (max 100), `sort_by`
(`created_at`/`updated_at`/`first_seen`/`last_seen`/`severity`/`confidence`),
`order` (`asc`/`desc`), and filters `severity`, `indicator_type`,
`source`, `category`, `country`.

Example:

```bash
curl "http://localhost:5000/api/threats?severity=high&indicator_type=URL&page=1&per_page=10"
```

```json
{
  "items": [
    {
      "id": 42,
      "indicator": "http://malicious-example.test/payload",
      "indicator_type": "URL",
      "category": "malware_download",
      "severity": "high",
      "confidence": 90,
      "country": null,
      "source": "URLhaus",
      "description": "Malware distribution URL (tags: elf, mirai)",
      "first_seen": "2026-07-01T09:02:05+00:00",
      "last_seen": "2026-07-01T09:02:05+00:00",
      "created_at": "2026-07-01T09:03:10+00:00",
      "updated_at": "2026-07-01T09:03:10+00:00"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total_items": 1,
  "total_pages": 1
}
```

## Scheduler

Three APScheduler interval jobs (AlienVault OTX, PhishTank, URLhaus)
run every `INGESTION_INTERVAL_MINUTES` (default 60), each firing once
immediately on startup so the database isn't empty for a full interval
after a fresh deploy. Set `SCHEDULER_ENABLED=false` to disable all three
(the test config already does this, so running tests never makes real
network calls).

Ingestion is dedup-aware: re-running a job updates `last_seen`,
`confidence`, and `severity` on indicators already in the database
instead of inserting duplicates, keyed on `(indicator, source)`.

## Known gaps / next steps

This phase intentionally ships a read-only, unauthenticated API to keep
scope matched to the spec. Before any real deployment:

- Add API-key or token auth in front of the `/api/*` routes.
- Add per-client rate limiting.
- Commit the generated `migrations/` folder (from `flask db init`) to
  version control instead of regenerating it per environment.
- Containerize (Dockerfile) if deploying somewhere other than a
  buildpack-based platform.
- Review each feed's terms of use / rate limits before any commercial
  redistribution of their data.
