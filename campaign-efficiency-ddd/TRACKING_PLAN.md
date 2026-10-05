# Event Inventory

`event_name` enum ที่เอกสารนี้เป็นเจ้าของ:

- `csv_import_succeeded`
- `csv_import_failed`
- `channel_filter_changed`
- `campaign_review_brief_generated`
- `campaign_review_brief_failed`

# Event Schema & Properties

| event_name | Required Properties |
|---|---|
| `csv_import_succeeded` | dataset_id, row_count |
| `csv_import_failed` | application_error_code, failing_row_count |
| `channel_filter_changed` | dataset_id, channel |
| `campaign_review_brief_generated` | dataset_id, brief_id |
| `campaign_review_brief_failed` | dataset_id, application_error_code |

- Do not include AI secret, raw CSV row payload, or full brief text in analytics events
- Event schema versioning: `null` — calibration owner: Developer if external analytics sink is added

# Identity & Session Rules

- MVP has no authenticated end-user identity
- Do not create a persistent cross-device user identifier
- Server request/session identifier may be ephemeral for debugging but must not be treated as a person identity
- `dataset_id` is a data resource identifier, not a user identity

# Consent & PDPA Gating

- Current events contain Non-personal business telemetry only under DATA_MODEL.md classification
- If future properties include Personal/Sensitive data, event emission must be gated by the lawful basis/consent rule defined after DATA_MODEL.md and SECURITY.md are updated
- Tracking is not required for core dashboard correctness and may be disabled without breaking business flows

# Tracking QA Checklist

- Event names match this document exactly
- Required properties are present and use correct resource identifiers
- No raw CSV content or secrets are emitted
- Failed import emits failure event without persisting partial dataset
- AI failure event does not block core dashboard
