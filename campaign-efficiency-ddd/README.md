# Project Name and Description

Campaign Efficiency Dashboard — web application for importing Campaign performance CSV, validating/persisting data to SQLite3, comparing Channel efficiency with Spend/Lead/Qualified Lead/CPL/CPQL/Qualification Rate, filtering Campaign detail, identifying the lowest eligible CPQL Channel, and optionally generating a saved AI Campaign Review Brief.

# Current Status (2026-10-05)

- Core MVP (all P0 requirements) and the AI bonus are implemented and verified end-to-end, including a real live call to OpenRouter and a full run against the 20,966-row reference dataset
- 53 automated tests passing, 97% coverage; Docker image builds and runs locally with verified persistence across container recreation
- Not yet done: push to the company Git repository (no remote configured in the build environment) and Coolify deployment (no Coolify credentials available) — see TASKS.md T-09

# Quick Start

1. Build the container: `docker build -t campaign-efficiency-dashboard .` — expected result: image build exits successfully.
2. Create a persistent data directory/volume and run: `docker run --rm -p 8000:8000 -e APP_ENV=development -e DATABASE_URL=sqlite:////data/app.db -v campaign-efficiency-data:/data campaign-efficiency-dashboard` — expected result: application listens on port 8000. Add `-e OPENROUTER_API_KEY=...` to enable the AI Campaign Review Brief bonus; omit it and the core dashboard still works, with the brief section reporting "not configured."
3. Open `http://localhost:8000/health` — expected result: healthy response with database reachable.
4. Open `http://localhost:8000/` — expected result: Campaign Efficiency Dashboard renders upload and analysis UI.
5. Upload the challenge CSV — expected result: valid dataset imports and dashboard shows KPI/channel data.
6. Run test command defined by the repository, expected to be `pytest` for this stack — expected result: all committed tests pass before deployment (53 passing, 97% coverage as of 2026-10-05).

For local (non-container) development: `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`, copy `.env.example` to `.env` and fill in values, then `.venv/bin/uvicorn app.main:app --reload`.

# Prerequisites

- Python 3.12 runtime for local non-container development
- Docker Engine compatible with the project Dockerfile
- SQLite3 provided through Python runtime/SQLAlchemy driver
- Coolify access for deployed environment
- Company AI endpoint credentials only when enabling the bonus workflow

# Installation

- Install Python dependencies from the repository lock/requirements file
- Configure `DATABASE_URL`
- For AI bonus configure `OPENROUTER_API_KEY` (secret), and optionally `OPENROUTER_BASE_URL`/`OPENROUTER_MODEL` to override the OpenRouter defaults
- Never commit real secret values

# Usage

- Import CSV using required schema documented in CONSTRAINTS.md (click "Upload CSV")
- Review KPI cards, the lowest eligible CPQL Channel callout, and both Channel comparison charts (CPQL and Qualification Rate)
- Use the Channel filter and the search box to narrow Campaign Details; results page at 25 rows at a time, so a 20,000+ row dataset stays responsive
- If AI (OpenRouter) is configured, click "Generate Brief" to produce and read a saved Campaign Review Brief (Facts / Items to Verify / Next Experiment Proposals); it survives a page refresh
- Undefined ratios display as N/A rather than zero
- Invalid CSV import is rejected atomically; the previously loaded dataset/dashboard stays intact

# Architecture Overview

- Read `ARCHITECTURE.md` for system/stack/deployment topology
- Read `DEPLOYMENT.md` for Coolify, variables, health and rollback procedure
- Read `AGENTS.md` for coding-agent rules; `CLAUDE.md` is provided as an identical convenience alias/copy for Claude Code
- SQLite is the MVP persistence layer; analytics are deterministic backend calculations

# Contributing

- Update the canonical owner document before changing an enum, metric contract, API or schema
- Keep PRD acceptance criteria and TESTING test cases traceable
- Do not merge code with failing P0 validation/tests
- Do not commit credentials or production database files

# License

- Company internal project. License/redistribution terms: `null` — owner: Company Repository Owner.
