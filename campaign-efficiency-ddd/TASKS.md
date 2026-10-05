# Task Breakdown

| Task | Traces To | Expected Output |
|---|---|---|
| T-01 Bootstrap FastAPI app + config | Architecture, FR-01 | Runnable service + `/health` |
| T-02 Create SQLite schema/migration | DATA_MODEL, FR-03 | datasets/campaigns/briefs tables |
| T-03 Implement CSV parser/validation + atomic import | FR-01..FR-03, AC-01 | Import endpoint + validation errors |
| T-04 Implement analytics service | FR-04..FR-08, FR-11, AC-02/05 | Dataset/Channel metrics |
| T-05 Build dashboard UI | FR-09..FR-10, CP-03..CP-05 | KPI, chart, table, filter, campaign detail |
| T-06 Add automated tests | AC-01..AC-06 | Passing pytest suite for core logic/HTTP |
| T-07 Dockerize + Coolify config | AC-07 | Container + persistent volume + health check |
| T-08 Integrate company AI client | FR-12..FR-14, CP-06 | Generate/save/read brief with graceful failure |
| T-09 Final validation + repository push | Challenge constraint | Test evidence, deployed URL, committed source |

# Task Sequence and Dependencies

```text
T-01 -> T-02 -> T-03 -> T-04 -> T-05 -> T-06 -> T-07 -> T-09
                                      \-> T-08 ---/
```

- T-08 starts only after core analytics contract exists; it must not block T-09 if AI credentials/contract are unavailable and bonus is intentionally deferred

# Definition of Done

- Code implements referenced PRD requirements without inventing conflicting rules
- Automated tests/validation for the task pass locally/container as applicable
- Error paths are handled and do not corrupt database state
- No secret is committed
- Relevant DDD contract remains consistent; owner document is updated before code when a contract changes
- User-visible core flow works in deployed environment for P0 requirements

`work_item_status` enum ที่เอกสารนี้เป็นเจ้าของ: `Not Started`, `In Progress`, `Done`, `Blocked`.

# Assignments and Estimates

| Task | Owner | Estimate | Status |
|---|---|---|---|
| T-01 Bootstrap FastAPI app + config | Claude Code | `null` | Done |
| T-02 Create SQLite schema/migration | Claude Code | `null` | Done |
| T-03 Implement CSV parser/validation + atomic import | Claude Code | `null` | Done |
| T-04 Implement analytics service | Claude Code | `null` | Done |
| T-05 Build dashboard UI | Claude Code | `null` | Done |
| T-06 Add automated tests | Claude Code | `null` | Done — 53 tests passing, 97% coverage |
| T-07 Dockerize + Coolify config | Claude Code | `null` | Done — image builds and runs locally; Coolify deploy itself is Blocked (no Coolify credentials in this environment) |
| T-08 Integrate company AI client | Claude Code | `null` | Done — OpenRouter (`anthropic/claude-sonnet-4.6`) integrated, live call verified 2026-10-05 |
| T-09 Final validation + repository push | Claude Code | `null` | In Progress — local validation/commit complete; push to company Git repository is Blocked (no remote configured in this environment) |
