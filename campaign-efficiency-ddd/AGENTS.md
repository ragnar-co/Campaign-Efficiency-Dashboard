# Project Overview

Build Campaign Efficiency Dashboard from the DDD documents in this directory. Treat these documents as contracts. Do not invent missing business rules. Core flow: CSV -> validate -> atomic SQLite persistence -> deterministic metrics -> Channel comparison/filter -> Docker/Coolify. AI brief is optional and must never be required for core analytics.

# Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x + SQLite3
- Jinja2 + vanilla JavaScript
- Chart.js
- pytest
- Docker/Coolify

# Coding Conventions

- Keep metric formulas in one backend analytics module/service
- Store money as integer satang; convert to THB at API/UI boundary
- Use Decimal for CSV money parsing before conversion
- Use typed request/response models where applicable
- Use repository/service separation sufficient to keep SQLite and AI clients out of templates/routes
- Preserve `null` for undefined ratios; UI renders `N/A`
- Overall coverage threshold: `null` — calibration owner: Developer after initial test run; test passing is required even while percentage threshold is uncalibrated

# Forbidden Patterns

- No metric calculations duplicated in JavaScript/templates
- No averaging Campaign-level CPL/CPQL to produce Channel metrics
- No partial import after any row validation failure
- No hardcoded secrets/API keys
- No user-supplied raw prompt forwarded directly to AI endpoint
- No raw HTML rendering of campaign/channel text
- No schema/enum invention outside the owning DDD document

# Testing Requirements

- Every PRD acceptance criterion must trace to at least one test/validation case in TESTING.md
- Every PERSONAS.md CP-ID must have at least one E2E scenario in TESTING.md
- Every API endpoint must have a contract test or smoke validation
- Include zero-denominator fixtures and invalid CSV fixtures
- Run tests before build/deploy and record outcome; do not fabricate passing results in documentation

# PDPA Rules

- Current product fields are Non-personal per DATA_MODEL.md
- Do not add personal data fields without updating DATA_MODEL.md classification and SECURITY/TRACKING rules first
- AI payload must be minimized to structured analytics facts and necessary labels
