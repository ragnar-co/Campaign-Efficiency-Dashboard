# Campaign Efficiency Dashboard

Web app for importing Campaign performance CSV, validating/persisting to SQLite3, comparing Channel efficiency (Spend / Leads / Qualified Leads / CPL / CPQL / Qualification Rate), drilling into Campaign detail, identifying the lowest eligible CPQL Channel, and optionally generating a saved AI Campaign Review Brief.

**Full product/architecture/API documentation lives in [`campaign-efficiency-ddd/`](campaign-efficiency-ddd/)** — treat those documents as the source of truth; this file is just the repo entry point. Start with [`campaign-efficiency-ddd/README.md`](campaign-efficiency-ddd/README.md) for current status, then [`PRD.md`](campaign-efficiency-ddd/PRD.md), [`API_SPEC.md`](campaign-efficiency-ddd/API_SPEC.md), [`DATA_MODEL.md`](campaign-efficiency-ddd/DATA_MODEL.md) as needed.

## Status (2026-10-05)

Core MVP + AI bonus implemented and verified end-to-end (live OpenRouter call + full run against the real 20,966-row reference dataset). 53 automated tests passing, 97% coverage. Docker image builds and runs with verified persistence. Not yet pushed to a remote or deployed to Coolify — see [`campaign-efficiency-ddd/TASKS.md`](campaign-efficiency-ddd/TASKS.md).

## Quick start

```bash
docker build -t campaign-efficiency-dashboard .
docker run --rm -p 8000:8000 \
  -e APP_ENV=development \
  -e DATABASE_URL=sqlite:////data/app.db \
  -e OPENROUTER_API_KEY=...            # optional — enables the AI brief bonus
  -v campaign-efficiency-data:/data \
  campaign-efficiency-dashboard
```

Open `http://localhost:8000/`, upload a CSV (schema in [`CONSTRAINTS.md`](campaign-efficiency-ddd/CONSTRAINTS.md)), and the dashboard populates.

### Local development (no Docker)

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in OPENROUTER_API_KEY if you want the AI bonus
.venv/bin/uvicorn app.main:app --reload
.venv/bin/pytest -q --cov=app
```

## Stack

Python 3.12 · FastAPI · SQLAlchemy 2.x · SQLite3 · Jinja2 + vanilla JS · Chart.js · OpenRouter (`anthropic/claude-sonnet-4.6`) · pytest · Docker

## Repository layout

```text
app/                      application source (FastAPI, services, templates, static)
tests/                    pytest suite
campaign-efficiency-ddd/  canonical product/architecture/API/security documentation
Raw Data/                 sample reference CSV (not committed — see .gitignore)
Dockerfile, .env.example  deployment/config
```

## Contributing

Update the canonical owner document in `campaign-efficiency-ddd/` *before* changing an enum, metric formula, schema, or API contract in code — see each document's stated owner. Never commit `.env` or real secret values.
