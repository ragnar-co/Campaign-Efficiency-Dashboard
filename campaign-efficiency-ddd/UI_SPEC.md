# Page Inventory

| Page | Purpose | Critical Paths |
|---|---|---|
| Dashboard | Upload CSV, show validation feedback, KPI cards, Channel chart/table, filter Campaign detail, lowest-CPQL highlight, AI brief panel | CP-01, CP-03, CP-04, CP-05, CP-06 |

# User Flow Diagrams

```text
Open Dashboard
  -> Upload CSV
  -> Validation
      -> invalid: show row/field errors, keep current dataset unchanged
      -> valid: persist dataset -> refresh dashboard
  -> Review KPIs + Channel comparison
  -> Select Channel -> inspect Campaign rows
  -> Optional: Generate Brief -> save -> render saved brief
```

Critical Path Trace:

| CP-ID | UI Surface | Success State | Failure State |
|---|---|---|---|
| CP-01 | Upload control + validation panel | Import success and dataset summary shown | Actionable row/field errors |
| CP-03 | KPI cards | All required metrics rendered; null ratios shown as N/A | Load error state with retry |
| CP-04 | Channel chart/table + best Channel callout | Same aggregation values in chart/table and lowest CPQL callout | N/A when no eligible Channel |
| CP-05 | Channel selector + Campaign table | Filtered rows match selected Channel | Empty state if no rows |
| CP-06 | AI brief panel | Saved Facts/Items to Verify/Next Experiment Proposals shown | AI error shown without hiding dashboard |

# Component Hierarchy

```text
DashboardPage
  UploadPanel
    FileInput
    ValidationResult
  KPIGrid
    MetricCard[]
  ChannelComparisonSection
    ChannelChart
    ChannelTable
    BestChannelCallout
  CampaignDetailSection
    ChannelFilter
    CampaignTable
  ReviewBriefSection
    GenerateBriefButton
    BriefStatus
    SavedBriefView
```

# State Management Plan

- Server is source of truth for persisted dataset and brief records
- Browser state only stores selected Channel and in-flight UI status
- No client-side duplication of metric formulas; UI renders server-calculated values
- Changing Channel must not mutate persisted data

# Responsive Breakpoints

- Desktop-first layout for challenge delivery
- Exact breakpoint values: `null` — calibration owner: UI Developer after testing target devices
- On narrow screens, KPI cards wrap, chart becomes horizontally scrollable if required, and Campaign table may scroll horizontally without hiding column labels

# Design Tokens

- Use CSS custom properties for spacing, typography, borders and semantic states
- Exact color palette/font scale: `null` — calibration owner: Designer/Frontend Developer
- Error/success states must not rely on color alone

# Accessibility Guidelines

- Every form control has visible label
- Upload/AI actions are keyboard operable
- Chart data is duplicated in accessible table form
- Validation errors identify field/row in text
- Focus moves to result/error summary after upload action
- Metric abbreviations CPL/CPQL have full-name labels or accessible descriptions

# i18n & Content Strategy

- MVP UI language: English technical metric labels are acceptable; business copy may be Thai if team chooses one language consistently
- Number formatting: THB for spend/cost metrics, integer counts for Leads, percentage format for Qualification Rate
- `null` metric values render as `N/A`, never `0`, to preserve denominator semantics
- Terminology must follow GLOSSARY.md
