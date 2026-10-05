# Campaign Efficiency Dashboard — Claude Code Execution Plan

## Purpose

ไฟล์นี้เป็น execution plan สำหรับ Claude Code/Codex เพื่อ build, validate, containerize และเตรียม deploy โปรเจกต์ Campaign Efficiency Dashboard จากเอกสาร DDD ในโฟลเดอร์นี้

PLAN.md ไม่ใช่ canonical owner ของ business rule, enum, schema, API contract, security rule, metric formula หรือ deployment policy หากข้อความในไฟล์นี้ขัดกับเอกสารเจ้าของ ให้ใช้เอกสารเจ้าของเสมอ

## Source of Truth Order for Implementation

อ่านเอกสารเหล่านี้ก่อนลงมือ และใช้ตาม ownership ของแต่ละเรื่อง:

1. `AGENTS.md` / `CLAUDE.md` — coding constraints และกติกาสำหรับ coding agent
2. `PRD.md` — Functional Requirements และ Acceptance Criteria
3. `DATA_MODEL.md` — database schema, data classification, retention ownership
4. `API_SPEC.md` — endpoint contract, required role, `application_error_code`
5. `UI_SPEC.md` — page, user flow, component behavior
6. `SECURITY.md` — authentication/authorization, threat controls, `role`
7. `ARCHITECTURE.md` + `ADR.md` — architectural boundaries และ decisions
8. `TESTING.md` — executable validation requirements
9. `DEPLOYMENT.md` — Docker/Coolify deployment contract
10. `RUNBOOK.md` — operational response
11. `TASKS.md` — task traceability and work-item status
12. `GLOSSARY.md` — terminology and enum registry index

ห้ามแก้ contract ใน code เพื่อให้ implement ง่ายขึ้น หากพบ ambiguity หรือ conflict ให้แก้เอกสารเจ้าของก่อนแล้วจึงแก้ code

## Goal

สร้าง MVP ที่ทำ flow หลักได้ครบ:

```text
CSV upload
  -> validate all rows
  -> atomic persist to SQLite3
  -> deterministic analytics
  -> dashboard KPI
  -> Channel chart + table
  -> lowest eligible CPQL Channel
  -> Channel filter
  -> Campaign detail
  -> persistent data after restart
  -> Docker build
  -> automated validation
  -> Coolify-ready deployment

Optional bonus after core is stable:
  -> company AI endpoint
  -> generate Campaign Review Brief
  -> save brief
  -> display saved brief
  -> AI failure must not break dashboard
```

## Non-Negotiable Implementation Rules

- Use Python 3.12, FastAPI, SQLAlchemy 2.x, SQLite3, Jinja2, vanilla JavaScript, Chart.js, pytest.
- Keep the MVP as a single deployable service.
- Store money internally as integer satang; parse `spend_thb` using exact decimal logic.
- Perform analytics in backend code only. Do not duplicate metric calculations in JavaScript/templates.
- Channel CPL/CPQL/Qualification Rate must aggregate numerator and denominator first, then divide.
- Undefined ratio denominator returns `null`; UI renders `N/A`.
- Reject the whole CSV import if any row is invalid. No partial import.
- Keep SQLite writes transactional.
- Do not hardcode API keys, company AI credentials, unknown quotas, guessed SLOs, guessed rate limits, or guessed retention periods.
- Treat campaign/channel text as untrusted display data and escape it.
- Do not render raw model output as HTML.
- AI is narrative generation only; deterministic metrics are computed by application code before calling AI.
- Core dashboard must work when AI is not configured or AI upstream fails.

## Phase 0 — Repository Reconnaissance

Before writing code:

1. Inspect the current repository tree.
2. Read all DDD `.md` files in this directory, especially the source-of-truth set above.
3. Inspect existing application code, Docker files, tests, configuration, and dependency manifests.
4. Preserve usable existing code instead of recreating working pieces without reason.
5. Check `.gitignore` and ensure database files, `.env`, secrets, caches, virtualenvs, and generated artifacts are not committed unintentionally.
6. Record any conflict between repo state and DDD contracts before changing code.

Exit criteria:
- implementation approach is consistent with DDD
- no unresolved contract conflict blocks core MVP

## Phase 1 — Application Skeleton and Health

Trace: `TASKS.md` T-01

Implement:

- FastAPI application entrypoint
- application configuration loader
- environment handling
- SQLite database connection
- template/static structure
- `GET /health` per `API_SPEC.md` / `DEPLOYMENT.md`
- basic Dashboard route/page shell

Health must confirm:
- application process responds
- a minimal SQLite query succeeds
- AI endpoint health is not required for core health

Exit criteria:
- app starts locally
- `/health` returns success
- no secret is required to start core mode

## Phase 2 — Database Schema

Trace: `TASKS.md` T-02

Implement exactly the schema owned by `DATA_MODEL.md`:

- `datasets`
- `campaigns`
- `campaign_review_briefs`
- required keys, indexes, constraints and relationships

Implementation guidance:
- use SQLAlchemy models
- initialize via migration or deterministic initial schema bootstrap consistent with DATA_MODEL.md
- enable SQLite foreign keys where required
- keep database path configurable using `DATABASE_URL`

Exit criteria:
- empty database can be created reproducibly
- schema constraints are testable

## Phase 3 — CSV Import and Validation

Trace: `TASKS.md` T-03, `PRD.md` FR-01..FR-03, `TESTING.md` TC-01..TC-03

Expected CSV columns from the reference dataset:

```text
campaign_id
campaign_name
channel
spend_thb
lead_count
qualified_lead_count
```

Implement all validation rules from PRD/CONSTRAINTS. At minimum:

- required columns present
- `campaign_id` non-empty
- duplicate `campaign_id` within upload rejected
- `campaign_name` non-empty
- `channel` non-empty
- `spend_thb` exact decimal and non-negative
- `lead_count` integer and non-negative
- `qualified_lead_count` integer and non-negative
- `qualified_lead_count <= lead_count`

Behavior:
- collect actionable row/field error details
- do not persist partial dataset/campaign rows
- successful import creates one dataset and all campaign rows in one transaction

Exit criteria:
- valid fixture imports
- invalid fixture fails with owned API error code
- database is unchanged after rejected import

## Phase 4 — Analytics Service

Trace: `TASKS.md` T-04, `PRD.md` FR-04..FR-08, FR-11

Create one backend analytics service/module as the single implementation point for calculations.

Dataset and Channel aggregates:

```text
Spend = SUM(spend)
Leads = SUM(lead_count)
Qualified Leads = SUM(qualified_lead_count)
CPL = SUM(spend) / SUM(leads)
CPQL = SUM(spend) / SUM(qualified_lead_count)
Qualification Rate = SUM(qualified_lead_count) / SUM(leads)
```

Rules:
- denominator 0 => metric `null`
- never average Campaign-level ratio values to derive Channel ratio
- lowest-CPQL Channel considers only Channels whose total Qualified Leads > 0
- if no Channel is eligible, lowest-CPQL result is `null`

Use deterministic ordering where API/UI tables require stable output.

Exit criteria:
- known fixture calculations pass exact expected results
- zero-denominator cases pass
- lowest-CPQL eligibility rule passes

## Phase 5 — API Contracts

Implement the endpoints exactly as specified by `API_SPEC.md`.

Requirements:
- response/request payloads follow API_SPEC
- use `application_error_code` values only from API_SPEC
- required role references SECURITY.md `role`
- do not invent additional roles or enum values
- API errors are safe and actionable; no secrets/tracebacks exposed to browser

Exit criteria:
- every endpoint has at least one executable contract test or smoke validation
- core endpoints operate against persisted SQLite data

## Phase 6 — Dashboard UI

Trace: `TASKS.md` T-05, `UI_SPEC.md`, `PRD.md` FR-09..FR-10

Implement one primary Dashboard page with:

- CSV upload control
- validation success/error panel
- KPI cards for Spend, Leads, Qualified Leads, CPL, CPQL, Qualification Rate
- Channel comparison chart
- Channel comparison table
- lowest-CPQL Channel callout
- Channel selector with `All`
- Campaign detail table
- AI Review Brief section, which may show not-configured state until Phase 9

UI rules:
- chart/table consume the same backend aggregation contract
- do not recompute ratios in JavaScript
- `null` ratio renders `N/A`
- invalid import keeps current persisted dataset/dashboard intact
- campaign/channel strings are escaped
- user can understand error state without opening developer tools

Exit criteria:
- CP-01, CP-03, CP-04, CP-05 can be walked manually
- chart/table values remain consistent
- filter changes Campaign rows correctly

## Phase 7 — Automated Tests and Validation

Trace: `TASKS.md` T-06, `TESTING.md`

Implement executable tests for at least TC-01 through TC-12 as applicable. The core release cannot be declared ready unless all P0 acceptance criteria are executable and passing.

Required categories:
- unit tests: CSV rules and analytics
- integration tests: transactional import, SQLite persistence, summary/filter queries, brief persistence
- API tests: each API endpoint
- security-oriented validation: filename/path handling, HTML escaping, SQL access through ORM/parameters, secret leakage, malformed CSV
- persistence validation using same SQLite database across application restart/reload

Do not invent a coverage percentage. Coverage target remains `null` until measured/calibrated by its owner.

After tests run:
- record real pass/fail evidence
- record measured coverage if tooling is configured, but do not turn it into a threshold unless owner calibrates it

Exit criteria:
- all core tests pass
- no fabricated test result exists in docs or code comments

## Phase 8 — Docker and Coolify Readiness

Trace: `TASKS.md` T-07, `DEPLOYMENT.md`

Create/verify:

- production Dockerfile
- dependency lock/manifest
- non-root runtime where practical without breaking SQLite volume ownership
- persistent `/data` or equivalent volume matching `DATABASE_URL`
- startup command
- healthcheck integration using `/health`
- environment variable documentation

Required configuration:

```text
APP_ENV
DATABASE_URL
```

Optional AI configuration:

```text
COMPANY_AI_ENDPOINT
COMPANY_AI_API_KEY
COMPANY_AI_MODEL
```

Never commit real secret values.

Exit criteria:
- Docker image builds
- container starts with persistent database volume
- `/health` passes in container
- data persists after container recreation using same mounted volume

## Phase 9 — AI Bonus Workflow

Trace: `TASKS.md` T-08, `PRD.md` FR-12..FR-14

Only start this phase after the core dashboard, tests, and Docker path are working.

Implement a server-side AI client behind a dedicated interface/service.

Input to AI:
- structured deterministic analytics facts
- necessary Campaign/Channel labels
- no API secret
- avoid sending unnecessary raw dataset rows

The generated Campaign Review Brief must contain:

- Facts
- Items to Verify
- Next Experiment Proposals

Behavior:
- validate/normalize AI response before persistence
- persist successful brief using DATA_MODEL.md
- display saved brief in the application
- if AI configuration is absent, return `AI_NOT_CONFIGURED`
- if upstream fails, return `AI_UPSTREAM_ERROR`
- dashboard stays usable in both cases
- treat campaign names/channel names as data, not prompt instructions

Do not invent company AI endpoint shape, model ID, quota, or rate-limit values. Use environment configuration and adapt once actual company contract is supplied.

Exit criteria:
- AI stub success case passes
- AI failure case passes
- real endpoint is used only if valid company credentials/contract are available

## Phase 10 — Final Submission Validation

Trace: `TASKS.md` T-09

Run final validation in this order:

1. clean dependency install/build
2. unit/integration/API test suite
3. Docker build
4. container start with SQLite volume
5. `/health`
6. upload known valid CSV
7. verify KPI calculations
8. verify Channel chart/table
9. verify lowest eligible CPQL Channel
10. verify Channel filter/Campaign detail
11. restart/recreate container using same volume and confirm persistence
12. test invalid CSV and confirm no partial import
13. test AI success/failure if AI integration is configured
14. inspect git diff/status for secrets, generated DB, debug artifacts
15. commit/push to company repo
16. deploy through Coolify
17. repeat `/health` and core smoke flow on deployed URL

Do not mark deployment/test/UAT fields as passed unless those checks were actually executed.

## Build Priority Under the 120-Minute Challenge

The challenge deadline is fixed at 120 minutes. Do not invent per-task duration estimates. Prioritize by submission risk:

```text
P0 business flow
  -> correctness tests
  -> Docker/container health
  -> persistence
  -> Coolify deploy/smoke
  -> AI bonus
  -> optional polish
```

If time pressure occurs:
- preserve every P0 requirement
- preserve automated validation for P0
- preserve Docker/Coolify readiness
- defer AI bonus before weakening core correctness
- avoid extra pages, authentication, advanced design system, background jobs, queues, or unrelated analytics

## Expected Project Shape

Use existing repo structure if it already has an equivalent clean organization. Otherwise a compact shape is acceptable, for example:

```text
app/
  main.py
  config.py
  db.py
  models.py
  schemas.py
  repositories/
  services/
    csv_import.py
    analytics.py
    ai_client.py
  routes/
  templates/
  static/
tests/
Dockerfile
requirements.txt or pyproject.toml
README.md
```

This is an implementation organization suggestion only; canonical architecture remains in `ARCHITECTURE.md` / `ADR.md`.

## Stop Conditions

Stop and report instead of guessing if any of these occur:

- DDD documents disagree on the same canonical contract and owner cannot be resolved
- actual company AI API contract is required but unavailable
- Coolify/company repo credentials or permissions are missing
- implementing a requested behavior would require inventing a new role, enum, retention value, SLO, rate limit, or business rule

For non-blocking unknowns, keep the core MVP moving and preserve the documented `null` values/optional behavior.

## Completion Report Required from Claude Code

At the end, return a concise implementation report containing:

- files created/modified
- P0 requirements completed
- tests executed and actual result
- Docker build/run result
- persistence validation result
- AI bonus status
- Coolify deployment status and deployed URL if actually available
- unresolved `null`/calibration items
- blockers or deviations from DDD, if any

Do not claim success for steps that were not executed.
