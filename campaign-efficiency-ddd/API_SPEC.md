# Endpoint List

| Method | Path | Purpose | Required role |
|---|---|---|---|
| GET | `/health` | Application/database health | `anonymous` |
| GET | `/` | Render dashboard | `anonymous` |
| POST | `/api/datasets/import` | Validate and import CSV atomically | `anonymous` |
| GET | `/api/datasets/{dataset_id}/summary` | Dataset KPI summary + lowest-CPQL Channel | `anonymous` |
| GET | `/api/datasets/{dataset_id}/channels` | Channel comparison metrics | `anonymous` |
| GET | `/api/datasets/{dataset_id}/campaigns` | Campaign detail with optional Channel filter | `anonymous` |
| POST | `/api/datasets/{dataset_id}/briefs` | Generate and save AI brief | `anonymous` |
| GET | `/api/datasets/{dataset_id}/briefs/latest` | Read latest saved brief | `anonymous` |

# Request and Response Schema

- Import: `multipart/form-data` with one CSV file; response contains `dataset_id`, `row_count`, validation summary
- Summary response: spend_thb, lead_count, qualified_lead_count, cpl, cpql, qualification_rate, best_cpql_channel; ratio/cost fields may be null when denominator semantics require it
- Channels response: list of channel rows using the same metric schema as summary
- Campaigns request: optional query `channel`; response contains persisted raw business fields plus derived per-campaign CPL/CPQL/Qualification Rate
- Brief create request: no raw model prompt accepted from browser; backend builds prompt from dataset analytics
- Brief response: id, dataset_id, generated_at, facts[], items_to_verify[], next_experiment_proposals[]

# Authentication

- Application authentication is not implemented in MVP; endpoint required role refers to SECURITY.md `role` enum value `anonymous`
- AI endpoint credential is server-to-server and never accepted from client request

# Error Codes

`application_error_code` enum ที่เอกสารนี้เป็นเจ้าของ:

- `INVALID_CSV_SCHEMA`
- `INVALID_CSV_ROW`
- `DUPLICATE_CAMPAIGN_ID`
- `DATASET_NOT_FOUND`
- `AI_NOT_CONFIGURED`
- `AI_UPSTREAM_ERROR`
- `INTERNAL_ERROR`

HTTP mapping: validation errors -> 400/422; missing dataset -> 404; AI configuration/upstream failure -> 503; unexpected server error -> 500.

# Rate Limiting

- Core read endpoints rate limit: `null` — calibration owner: Platform Owner
- CSV import rate limit: `null` — calibration owner: Platform Owner
- AI brief generation rate limit: `null` — calibration owner: Company AI Platform Owner based on assigned quota
- Do not hardcode guessed quota values

# Versioning Strategy

- MVP endpoints live under current unversioned `/api` namespace for challenge simplicity
- Before incompatible external consumers exist, breaking changes may be applied with coordinated app release
- If an external consumer is introduced, move API to explicit versioned namespace before breaking change
