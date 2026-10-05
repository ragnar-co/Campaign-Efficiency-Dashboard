# Authentication and Authorization

`role` enum ที่เอกสารนี้เป็นเจ้าของ: `anonymous`.

- MVP does not implement application authentication per ADR-003
- All application endpoints therefore use required role `anonymous`; API_SPEC.md references this enum value and does not redefine roles
- This does not mean the application is safe for unrestricted public exposure; Coolify/network access policy must follow company environment rules
- If authentication is added, SECURITY.md must be revised before API endpoint permissions change

# PDPA Compliance Checklist

- Current campaign dataset classified Non-personal in DATA_MODEL.md
- No user profile, email, phone or other direct personal identifier is part of current schema
- AI payload must exclude unnecessary raw row data and secrets
- If a future upload adds Personal/Sensitive fields, stop implementation until DATA_MODEL.md classification, lawful basis, erasure and tracking gates are updated

# Threat Model

| Threat | Control |
|---|---|
| Malformed/malicious CSV | Strict parser, schema validation, row validation, upload size control when calibrated |
| Path traversal via filename | Never use client filename as server path; generate internal identifier |
| SQL injection | ORM/parameterized queries only |
| Formula/HTML injection in display values | Escape campaign/channel text in templates; never render untrusted HTML |
| Secret leakage | AI key only from secret store/environment; redact logs/errors |
| AI prompt injection from campaign text | Treat campaign fields as data, not instructions; prompt uses delimited structured JSON and fixed system instruction |
| AI outage/quota failure | Isolate AI action; dashboard remains operational |

# Encryption Strategy

- In transit: HTTPS terminated by Coolify/reverse proxy in deployed environments
- At rest: SQLite volume encryption capability depends on hosting platform; requirement = `null` — calibration owner: Platform/Security Owner
- Secrets are stored outside repository in Coolify secret/environment management

# Audit Logging Requirements

- Log security-relevant actions: import success/failure, AI request success/failure, unhandled server error
- Do not log AI credentials or raw CSV bodies
- Audit log retention: `null` — calibration owner: Security/Platform Owner
- Erasure responsibility for audit records: Security/Platform Owner; current dataset is Non-personal so user-erasure workflow is not applicable to product data

# Incident Response Plan

- On suspected secret exposure: disable/rotate affected AI credential in secret store, redeploy, inspect logs, and record incident
- On corrupted database/import defect: stop writes, snapshot database, restore/rebuild per RUNBOOK.md
- On public exposure contrary to company policy: restrict route at deployment layer first, then investigate access logs
- Incident severity values and escalation thresholds are owned by RUNBOOK.md
