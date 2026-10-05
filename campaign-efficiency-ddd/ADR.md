# Decision Log

| ADR | Title | adr_status | Decision |
|---|---|---|---|
| ADR-001 | Single-service FastAPI architecture | Accepted | Use one FastAPI deployable containing UI, API, validation and analytics |
| ADR-002 | SQLite3 for MVP persistence | Accepted | Use SQLite3 on persistent volume; isolate persistence behind repository layer |
| ADR-003 | No application login for challenge MVP | Accepted | Do not implement end-user authentication; deployment perimeter is responsible for exposure control |
| ADR-004 | Deterministic analytics, AI for narrative only | Accepted | Backend computes facts/metrics; AI only drafts brief from structured facts |
| ADR-005 | Reject invalid CSV atomically | Accepted | Validate all rows before commit; any invalid row rejects the whole upload |

`adr_status` enum ที่เอกสารนี้เป็นเจ้าของ: `Proposed`, `Accepted`, `Deprecated`, `Superseded`.

# Template

- **ADR ID:** stable identifier
- **Title:** decision name
- **Status:** value from `adr_status`
- **Context:** problem/constraint forcing a decision
- **Options:** viable alternatives considered
- **Decision:** selected approach
- **Consequences:** positive/negative impact and follow-up
- **Supersedes/Superseded by:** ADR relationship when applicable

# Index

- ADR-001 supports ARCHITECTURE.md single deployable and the 120-minute delivery constraint
- ADR-002 supports SQLite3 requirement and Docker/Coolify deployment
- ADR-003 is the security boundary assumption consumed by SECURITY.md and API_SPEC.md
- ADR-004 constrains AI implementation and testability
- ADR-005 defines import transaction behavior required by PRD AC-01
