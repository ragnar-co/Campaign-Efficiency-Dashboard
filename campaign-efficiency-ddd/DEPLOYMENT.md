# Environment Setup

- `development`: local application + local SQLite file
- `staging`: optional isolated Coolify service/volume if time and company setup allow
- `production`: Coolify service with persistent SQLite volume
- Environment names must use ARCHITECTURE.md `environment` enum

# CI/CD Pipeline

1. Pull/checkout company repository
2. Install/build Docker image
3. Run automated tests inside reproducible environment
4. Fail deployment if tests fail
5. Deploy image through Coolify
6. Attach persistent SQLite volume
7. Inject environment variables/secrets
8. Verify `/health`
9. Smoke-test upload -> dashboard -> Channel filter; AI brief only if configured

# Environment Variables

| Variable | Required | Secret | Example | Source/Notes |
|---|---|---|---|---|
| `APP_ENV` | yes | no | `production` | value from ARCHITECTURE `environment` enum |
| `DATABASE_URL` | yes | no | `sqlite:////data/app.db` | persistent volume path |
| `OPENROUTER_API_KEY` | only for AI bonus | yes | `***` | Coolify secret store/environment secret; never committed |
| `OPENROUTER_BASE_URL` | no (defaults if unset) | no | `https://openrouter.ai/api/v1` | OpenRouter API base URL |
| `OPENROUTER_MODEL` | no (defaults if unset) | no | `anthropic/claude-sonnet-4.6` | OpenRouter model identifier |

- AI provider decision: OpenRouter (`https://openrouter.ai/api/v1/chat/completions`), chosen as the company AI endpoint for the Campaign Review Brief bonus (supersedes the earlier generic `COMPANY_AI_*` placeholder names)
- Secret store: Coolify environment/secret management
- Secret rotation cadence: `null` — calibration owner: Security Owner

# Rollback Procedure

1. Stop new deployment traffic/write activity if data migration risk exists
2. Select previously known-good application image in Coolify
3. If schema change is backward-compatible, deploy previous image and keep database
4. If migration is irreversible, do not run destructive rollback; apply a roll-forward migration/fix from a database snapshot
5. Start service and verify `/health`
6. Smoke-test latest persisted dataset and Channel filter
7. Verify no new application errors appear before considering rollback complete

# Health Check Endpoints

- `GET /health`
- Healthy when application process responds success and a minimal SQLite query succeeds
- AI endpoint availability is not part of core health because AI is optional

# Zero-downtime Deployment

`deployment_strategy` enum ที่เอกสารนี้เป็นเจ้าของ: `recreate`.

- MVP uses `recreate` deployment because SQLite single-writer/persistent-file semantics make multi-replica rolling deployment undesirable without further design
- True zero-downtime target: `null` — calibration owner: Platform Owner; do not claim zero downtime for this MVP
- Persistent volume must not be deleted during application image replacement
