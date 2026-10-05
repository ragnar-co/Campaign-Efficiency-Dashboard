# Unreleased

### Added
- FastAPI application with `/health`, server-rendered dashboard, and SQLite3 persistence (`datasets`, `campaigns`, `campaign_review_briefs` per DATA_MODEL.md)
- CSV import/validation (FR-01..FR-03): atomic all-or-nothing persistence, actionable row/field errors, `INVALID_CSV_SCHEMA`/`INVALID_CSV_ROW`/`DUPLICATE_CAMPAIGN_ID` error codes
- Deterministic analytics service (FR-04..FR-08, FR-11): Spend/Leads/Qualified Leads/CPL/CPQL/Qualification Rate, aggregate-then-divide (never averaged per-Campaign), null-safe zero-denominator handling, lowest-eligible-CPQL Channel
- Dashboard UI: KPI cards, lowest-CPQL Channel callout (with a real computed "% lower than overall average" stat), two Channel comparison charts (CPQL and Qualification Rate, Chart.js with value-labeled bars), Channel Comparison table, Campaign Details table with Channel filter plus client-side search and pagination (25 rows/page) for datasets up to tens of thousands of rows
- Polished light SaaS visual design: validated categorical color palette per channel (consistent across both charts and the table), rounded cards, accessible N/A rendering for undefined ratios
- AI Campaign Review Brief bonus (FR-12..FR-14): OpenRouter integration (`OpenRouterClient` behind a provider-agnostic `AIClient` interface), structured Facts/Items to Verify/Next Experiment Proposals, persisted to `campaign_review_briefs` and displayed in-app, survives page refresh via a restored last-dataset id
- Docker image (non-root user, `/data` volume, `/health`-based HEALTHCHECK) verified to build and run locally with persistence across container recreation
- Automated test suite: 53 tests (unit/integration/API/persistence/security/AI-adapter), 97% coverage, including a full run against the real 20,966-row reference dataset

### Changed
- `COMPANY_AI_ENDPOINT`/`COMPANY_AI_API_KEY`/`COMPANY_AI_MODEL` placeholder env vars replaced with the concrete OpenRouter contract: `OPENROUTER_API_KEY` (secret), `OPENROUTER_BASE_URL` (default `https://openrouter.ai/api/v1`), `OPENROUTER_MODEL` (default `anthropic/claude-sonnet-4.6`) — see DEPLOYMENT.md/CONSTRAINTS.md

### Fixed
- `[hidden]` attribute was being overridden by grid/flex `display` rules on the same element, so empty-state sections briefly showed stale content before any CSV was imported
- Browser's default focus-ring rendered as a stray blue box around the upload status banner when focus moved there for accessibility; now styled to match the banner's own color

# Version History

- No released application version has been verified yet. Move entries from Unreleased only after a deployed release is confirmed.
