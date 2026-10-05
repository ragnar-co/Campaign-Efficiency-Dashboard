# Project Name and Description

Campaign Efficiency Dashboard — web application for importing Campaign performance CSV, validating/persisting data to SQLite3, comparing Channel efficiency with Spend/Lead/Qualified Lead/CPL/CPQL/Qualification Rate, filtering Campaign detail, identifying the lowest eligible CPQL Channel, and optionally generating a saved AI Campaign Review Brief.

# Quick Start

1. Build the container: `docker build -t campaign-efficiency-dashboard .` — expected result: image build exits successfully.
2. Create a persistent data directory/volume and run: `docker run --rm -p 8000:8000 -e APP_ENV=development -e DATABASE_URL=sqlite:////data/app.db -v campaign-efficiency-data:/data campaign-efficiency-dashboard` — expected result: application listens on port 8000.
3. Open `http://localhost:8000/health` — expected result: healthy response with database reachable.
4. Open `http://localhost:8000/` — expected result: Campaign Efficiency Dashboard renders upload and analysis UI.
5. Upload the challenge CSV — expected result: valid dataset imports and dashboard shows KPI/channel data.
6. Run test command defined by the repository, expected to be `pytest` for this stack — expected result: all committed tests pass before deployment.

# Prerequisites

- Python 3.12 runtime for local non-container development
- Docker Engine compatible with the project Dockerfile
- SQLite3 provided through Python runtime/SQLAlchemy driver
- Coolify access for deployed environment
- Company AI endpoint credentials only when enabling the bonus workflow

# Installation

- Install Python dependencies from the repository lock/requirements file
- Configure `DATABASE_URL`
- For AI bonus configure `COMPANY_AI_ENDPOINT`, `COMPANY_AI_API_KEY`, and `COMPANY_AI_MODEL` only if required by company endpoint
- Never commit real secret values

# Usage

- Import CSV using required schema documented in CONSTRAINTS.md
- Review KPI cards and Channel comparison
- Use Channel filter to inspect Campaign detail
- Review lowest eligible CPQL Channel callout
- If AI is configured, generate and read saved Campaign Review Brief
- Undefined ratios display as N/A rather than zero

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
