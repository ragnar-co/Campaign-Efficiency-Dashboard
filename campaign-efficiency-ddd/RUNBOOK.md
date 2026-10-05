# Daily Operations

- Verify application `/health`
- Confirm persistent SQLite volume is mounted and writable before accepting imports
- Review application errors for failed imports or AI upstream errors
- Do not treat AI failure as core application outage if dashboard remains healthy

# Monitoring and Alerts

| Signal | Threshold | Channel | Owner | Response |
|---|---|---|---|---|
| Application availability | `null` — calibrate against ARCHITECTURE availability SLO | `null` — Platform Owner | Platform Owner | Check container/reverse proxy/database; restore service |
| Dashboard response time | `null` — calibrate against ARCHITECTURE response-time SLO | `null` — Platform Owner | Developer | Inspect DB/query/load and recent deploy |
| CSV import duration/failure | `null` — calibrate against ARCHITECTURE import SLO | `null` — Platform Owner | Developer | Inspect validation/parser/database transaction |
| AI upstream failures | `null` — calibration owner: Company AI Platform Owner | `null` — Platform Owner | Developer/AI Platform Owner | Confirm configuration/quota/upstream; core dashboard stays online |

# Troubleshooting Guide

- Import rejected: inspect returned application_error_code and row/field detail; fix source CSV and re-upload
- Dashboard shows N/A for ratio: confirm denominator is zero; this is expected semantic behavior, not calculation failure
- Database locked/unavailable: stop duplicate writers, verify volume/path/permissions, restart single service after integrity check
- AI_NOT_CONFIGURED: set required AI environment variables or leave bonus feature disabled
- AI_UPSTREAM_ERROR: retry only after checking quota/upstream status; do not recompute core metrics via AI
- Missing data after redeploy: verify persistent volume was mounted at same database path before writing new data

# Backup and Recovery

- Backup mechanism: copy/snapshot SQLite database while writes are quiesced or use SQLite online-backup method
- Backup frequency: `null` — calibration owner: Platform Owner
- RTO/RPO are constrained in CONSTRAINTS.md and currently `null`
- Restore verification: start isolated service against restored database, run integrity check, open latest dataset summary and Channel filter, then record result

# Incident Response

`incident_severity` enum ที่เอกสารนี้เป็นเจ้าของ: `P0` = site down/core unusable, `P1` = degraded core flow, `P2` = minor/non-core issue.

- SLA per severity: `null` — calibration owner: Platform/Security Owner
- Escalation chain: `null` — calibration owner: Company Team Lead; must name actual contact/channel before production readiness
- AI-only outage is normally P2 unless company business rule says otherwise because core dashboard remains functional
- Secret exposure follows SECURITY.md incident plan immediately

# Scaling Procedures

- Do not add multiple app replicas writing the same SQLite file as a quick fix
- First measure import/query bottleneck with reference dataset
- If concurrency/storage limits are reached, migrate persistence to a server database behind existing repository interface and record new ADR
- Scale AI independently through request throttling/queue only after quota and rate limit are calibrated
