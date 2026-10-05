# System Diagram

```text
Browser
  |
  | HTTP
  v
FastAPI application
  |-- CSV validation/import service
  |-- deterministic analytics service
  |-- server-rendered dashboard + JSON endpoints
  |-- AI brief service (optional)
  |
  +--> SQLite3 persistent database
  |
  +--> Company AI HTTP endpoint
```

# Tech Stack Decisions

- Python 3.12
- FastAPI for HTTP application/API
- SQLAlchemy 2.x for SQLite access and transaction handling
- Jinja2 + vanilla JavaScript for server-rendered UI and small interactions
- Chart.js for Channel comparison visualization
- pytest for automated tests
- Docker single-container application; SQLite database mounted on persistent volume
- No separate frontend build pipeline in MVP to reduce deployment complexity

# Deployment Architecture

`environment` enum ที่เอกสารนี้เป็นเจ้าของ: `development`, `staging`, `production`.

- `development`: local Docker or local Python process with local SQLite file
- `staging`: optional Coolify service using isolated persistent volume and non-production secrets
- `production`: Coolify service using persistent SQLite volume and production AI secret when bonus feature is enabled
- Health endpoint is exposed by application and used by Docker/Coolify health checks

# Scalability Strategy

- MVP optimizes for a single process and uploaded datasets comparable to the provided CSV, not horizontal write scaling
- SQLite access is centralized through the application; long-running background workers are out of scope
- If concurrent writes or dataset size exceeds measured limits, migrate storage behind repository/service boundaries rather than embedding SQLite-specific logic in UI code
- Cache TTL: `null` — calibration owner: Developer; no cache is required for MVP correctness

# Third-party Integrations

- Coolify: deployment/orchestration target
- Company Git repository: source control/CI source
- Company AI endpoint: optional Campaign Review Brief generation; integration must be isolated behind an AI client interface
- No ad-platform API integration in MVP

# Observability & SLOs

- Structured application logs must include request path, result status, dataset_id when applicable, and error code; never log AI secrets
- `/health` reports application process and database reachability
- Availability SLO: `null` — calibration owner: Platform Owner
- Dashboard response-time SLO: `null` — calibration owner: Developer; measure with provided reference CSV on deployed environment
- CSV import duration SLO: `null` — calibration owner: Developer; measure with provided reference CSV on deployed environment
- Each SLO above must have paired alert handling in RUNBOOK.md before production readiness
