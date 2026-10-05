# Test Strategy

- Unit tests: CSV validation and analytics formulas
- Integration tests: SQLite transaction/import persistence, summary queries, Channel filtering, brief persistence
- API contract tests: every API_SPEC endpoint
- E2E/smoke tests: critical paths CP-01..CP-06; CP-06 may be exercised with AI client stub when real quota is unavailable
- Deployment smoke validation: `/health` + core dashboard flow on Coolify

# Test Cases

| Test ID | Trace | Case |
|---|---|---|
| TC-01 | AC-01, CP-01 | Valid CSV imports atomically and returns dataset id |
| TC-02 | AC-01, CP-01 | Missing required column rejects file with `INVALID_CSV_SCHEMA` |
| TC-03 | AC-01, CP-01 | Invalid numeric/qualified>lead/duplicate campaign_id rejects whole file and persists no partial dataset |
| TC-04 | AC-02, CP-03 | Known fixture returns exact totals and ratios |
| TC-05 | AC-02, CP-03 | lead denominator 0 -> CPL/Qualification Rate null; qualified denominator 0 -> CPQL null |
| TC-06 | AC-03, CP-04 | Channel API values equal values used by table/chart payload |
| TC-07 | AC-05, CP-04 | Lowest CPQL excludes Channel with zero Qualified Leads |
| TC-08 | AC-04, CP-05 | Channel filter returns only selected Channel; All returns full dataset |
| TC-09 | AC-06, CP-02 | Imported data persists across application restart/reload using same SQLite volume |
| TC-10 | AC-07 | `/health` passes on deployed container and dashboard loads |
| TC-11 | AC-08, CP-06 | AI stub success creates/saves/reads structured brief |
| TC-12 | AC-08, CP-06 | AI error returns controlled error and dashboard remains usable |

# Coverage Requirements

- Overall coverage threshold is owned by AGENTS.md and currently `null`; TESTING.md does not redefine it
- Unit layer target: `null` — calibration owner: Developer; measurement method: pytest coverage report; enforcement: guideline until calibrated
- Integration layer target: `null` — calibration owner: Developer; measurement method: pytest coverage/report + explicit contract case count; enforcement: guideline until calibrated
- Regardless of percentage, all P0 acceptance criteria and every API endpoint must have executable validation before submission
- Actual measured coverage (informational only, not a gate): 97% line coverage, 53 passing tests (`pytest -q --cov=app`), last measured 2026-10-05. Uncovered lines are almost entirely the real-network branch of `OpenRouterClient` (untestable without spending live quota) and a few defensive/unreachable error branches.

# Security Test Results

- Planned checks: filename/path traversal, HTML escaping, SQL injection resistance via parameterized access, secret absence from repository/log response, malformed CSV handling
- Actual result (executed 2026-10-05, `tests/test_security.py`): all pass —
  - Path traversal: client filename `../../../../etc/passwd.csv` imports successfully and no file is written outside the app; filename is only ever stored as a DB text label, never used as a filesystem path
  - SQL injection: `channel=Email' OR '1'='1` query param returns zero rows (parameterized ORM query), no error
  - Malformed/non-CSV upload (raw binary bytes): rejected with 422, never a 500
  - Secret leakage: `OPENROUTER_API_KEY` value never appears in `/health`, `/`, summary, or brief response bodies, including on AI upstream failure
  - HTML escaping: campaign/channel text is rendered via `textContent` only in `app/static/app.js`, never `innerHTML`/raw interpolation — verified by manual browser check with a campaign name containing `<b>Test</b>`, which rendered as literal text

# Performance Test Results

- Benchmark dataset: uploaded CSV with 20,966 rows (`Raw Data/ant_campaign_efficiency_mock_2_55MB.csv`, ~2.55 MB)
- Targets are owned by PRD/ARCHITECTURE and currently `null` (no SLO to pass/fail against)
- Actual measured results (2026-10-05, local `uvicorn` dev server, Apple Silicon Mac, not the deployed container — re-measure on the real Coolify host before relying on these for capacity planning):
  - CSV import (validate + atomic persist, 20,966 rows): ~0.74s
  - `GET /summary`: ~0.02s
  - `GET /channels`: ~0.01s
  - `GET /campaigns?channel=Email` (2,575 rows): ~0.03s
  - `GET /campaigns` (all 20,966 rows, no filter): ~0.27s
  - Process RSS after import + several queries: ~131 MB
  - Live OpenRouter brief generation call (`anthropic/claude-sonnet-4.6`, full 7-channel dataset facts): ~24s end-to-end

# UAT Sign-off

- Growth Marketing Analyst: `null` — sign-off owner: challenge submitter/reviewer
- Growth Marketing Manager: `null` — sign-off owner: challenge submitter/reviewer
- Required UAT walk-through: upload valid CSV, inspect KPI/chart/table, filter Channel, confirm lowest CPQL; AI brief when bonus integration is configured
- Developer self-walkthrough completed 2026-10-05 in a real browser against the full 20,966-row dataset: KPI cards, both channel charts, Channel Comparison table, Campaign Details with search/pagination, Channel filter, and a live-generated AI brief (OpenRouter) all verified against independently recomputed ground truth (see CHANGELOG.md) — this is a developer check, not the formal UAT sign-off above
