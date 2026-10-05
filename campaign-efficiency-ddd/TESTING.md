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

# Security Test Results

- Planned checks: filename/path traversal, HTML escaping, SQL injection resistance via parameterized access, secret absence from repository/log response, malformed CSV handling
- Actual result: `null` — execution owner: Developer; fill from real test run before claiming launch readiness

# Performance Test Results

- Benchmark dataset: uploaded CSV with 20,966 rows
- Measurements to capture: import duration, dashboard summary duration, Channel filter duration, memory usage
- Targets are owned by PRD/ARCHITECTURE and currently `null`
- Actual measured results: `null` — execution owner: Developer on deployed/container environment

# UAT Sign-off

- Growth Marketing Analyst: `null` — sign-off owner: challenge submitter/reviewer
- Growth Marketing Manager: `null` — sign-off owner: challenge submitter/reviewer
- Required UAT walk-through: upload valid CSV, inspect KPI/chart/table, filter Channel, confirm lowest CPQL; AI brief when bonus integration is configured
