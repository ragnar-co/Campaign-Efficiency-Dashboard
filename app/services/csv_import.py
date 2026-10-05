"""CSV parsing, validation, and atomic persistence.

Rules sourced from PRD.md FR-01..FR-03, CONSTRAINTS.md Technical Constraints,
and CLAUDE.md money-handling conventions. Any single invalid row rejects the
whole file (ADR-005); no partial dataset/campaign rows are ever persisted.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.errors import ApplicationError, ApplicationErrorCode
from app.models import Dataset
from app.repositories.dataset_repo import create_dataset_with_campaigns

REQUIRED_COLUMNS = [
    "campaign_id",
    "campaign_name",
    "channel",
    "spend_thb",
    "lead_count",
    "qualified_lead_count",
]


@dataclass
class RowError:
    row: int
    field: str
    message: str
    application_error_code: str

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "field": self.field,
            "message": self.message,
            "application_error_code": self.application_error_code,
        }


@dataclass
class ParsedCsv:
    valid_rows: list[dict] = field(default_factory=list)
    errors: list[RowError] = field(default_factory=list)


def _parse_money_to_satang(raw: str) -> int:
    value = Decimal(raw)
    if value < 0:
        raise ValueError("spend_thb must not be negative")
    scaled = value * 100
    if scaled != scaled.to_integral_value():
        raise ValueError("spend_thb must have at most 2 decimal places")
    return int(scaled.to_integral_value())


def _parse_nonneg_int(raw: str) -> int:
    if not raw.lstrip("-").isdigit():
        raise ValueError("must be a non-negative integer")
    value = int(raw)
    if value < 0:
        raise ValueError("must be a non-negative integer")
    return value


def parse_and_validate_csv(raw_bytes: bytes) -> ParsedCsv:
    text = raw_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))

    fieldnames = reader.fieldnames or []
    missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        raise ApplicationError(
            ApplicationErrorCode.INVALID_CSV_SCHEMA,
            f"CSV is missing required column(s): {', '.join(missing)}",
        )

    parsed = ParsedCsv()
    seen_campaign_ids: set[str] = set()

    for line_no, raw_row in enumerate(reader, start=2):
        values = {col: (raw_row.get(col) or "").strip() for col in REQUIRED_COLUMNS}

        if all(v == "" for v in values.values()):
            continue  # blank trailing line, not a data row

        row_has_error = False

        campaign_id = values["campaign_id"]
        campaign_name = values["campaign_name"]
        channel = values["channel"]

        if not campaign_id:
            parsed.errors.append(
                RowError(line_no, "campaign_id", "campaign_id must not be empty",
                          ApplicationErrorCode.INVALID_CSV_ROW.value)
            )
            row_has_error = True
        else:
            # Track every non-empty campaign_id seen so far, regardless of
            # whether THIS row has other errors, so a later duplicate of an
            # otherwise-invalid row is still caught (FR-02 duplicate check is
            # independent of other field validity).
            if campaign_id in seen_campaign_ids:
                parsed.errors.append(
                    RowError(
                        line_no,
                        "campaign_id",
                        f"duplicate campaign_id '{campaign_id}' within this file",
                        ApplicationErrorCode.DUPLICATE_CAMPAIGN_ID.value,
                    )
                )
                row_has_error = True
            seen_campaign_ids.add(campaign_id)

        if not campaign_name:
            parsed.errors.append(
                RowError(line_no, "campaign_name", "campaign_name must not be empty",
                          ApplicationErrorCode.INVALID_CSV_ROW.value)
            )
            row_has_error = True

        if not channel:
            parsed.errors.append(
                RowError(line_no, "channel", "channel must not be empty",
                          ApplicationErrorCode.INVALID_CSV_ROW.value)
            )
            row_has_error = True

        spend_satang: int | None = None
        try:
            spend_satang = _parse_money_to_satang(values["spend_thb"])
        except (InvalidOperation, ValueError) as exc:
            parsed.errors.append(
                RowError(line_no, "spend_thb", str(exc), ApplicationErrorCode.INVALID_CSV_ROW.value)
            )
            row_has_error = True

        lead_count: int | None = None
        try:
            lead_count = _parse_nonneg_int(values["lead_count"])
        except ValueError as exc:
            parsed.errors.append(
                RowError(line_no, "lead_count", str(exc), ApplicationErrorCode.INVALID_CSV_ROW.value)
            )
            row_has_error = True

        qualified_lead_count: int | None = None
        try:
            qualified_lead_count = _parse_nonneg_int(values["qualified_lead_count"])
        except ValueError as exc:
            parsed.errors.append(
                RowError(
                    line_no,
                    "qualified_lead_count",
                    str(exc),
                    ApplicationErrorCode.INVALID_CSV_ROW.value,
                )
            )
            row_has_error = True

        if (
            lead_count is not None
            and qualified_lead_count is not None
            and qualified_lead_count > lead_count
        ):
            parsed.errors.append(
                RowError(
                    line_no,
                    "qualified_lead_count",
                    "qualified_lead_count must not exceed lead_count",
                    ApplicationErrorCode.INVALID_CSV_ROW.value,
                )
            )
            row_has_error = True

        if row_has_error:
            continue

        parsed.valid_rows.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "channel": channel,
                "spend_satang": spend_satang,
                "lead_count": lead_count,
                "qualified_lead_count": qualified_lead_count,
            }
        )

    return parsed


def import_csv(session: Session, source_filename: str, raw_bytes: bytes) -> Dataset:
    """Validate the whole file, then persist atomically if and only if there
    are zero row errors. Never writes a partial dataset (ADR-005, FR-02/FR-03)."""
    parsed = parse_and_validate_csv(raw_bytes)

    if parsed.errors:
        codes_present = {e.application_error_code for e in parsed.errors}
        top_code = (
            ApplicationErrorCode.DUPLICATE_CAMPAIGN_ID
            if ApplicationErrorCode.DUPLICATE_CAMPAIGN_ID.value in codes_present
            else ApplicationErrorCode.INVALID_CSV_ROW
        )
        raise ApplicationError(
            top_code,
            f"CSV import rejected: {len(parsed.errors)} invalid row(s)",
            errors=[e.to_dict() for e in parsed.errors],
        )

    if not parsed.valid_rows:
        raise ApplicationError(
            ApplicationErrorCode.INVALID_CSV_SCHEMA,
            "CSV contains no data rows",
        )

    return create_dataset_with_campaigns(session, source_filename, parsed.valid_rows)
