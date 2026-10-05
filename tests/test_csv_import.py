"""CSV validation/import tests — TC-01, TC-02, TC-03, AC-01."""

from __future__ import annotations

import pytest

from app.errors import ApplicationError, ApplicationErrorCode
from app.services.csv_import import import_csv, parse_and_validate_csv
from tests.conftest import INVALID_ROWS_CSV, MISSING_COLUMN_CSV, VALID_CSV


def test_valid_csv_parses_with_no_errors():
    parsed = parse_and_validate_csv(VALID_CSV)
    assert parsed.errors == []
    assert len(parsed.valid_rows) == 3


def test_missing_required_column_raises_invalid_csv_schema():
    with pytest.raises(ApplicationError) as exc_info:
        parse_and_validate_csv(MISSING_COLUMN_CSV)
    assert exc_info.value.code == ApplicationErrorCode.INVALID_CSV_SCHEMA


@pytest.mark.parametrize(
    ("row", "expected_field"),
    [
        (b"C9,,Email,100.00,10,1\n", "campaign_name"),
        (b"C9,Name,,100.00,10,1\n", "channel"),
        (b"C9,Name,Email,abc,10,1\n", "spend_thb"),
        (b"C9,Name,Email,10.005,10,1\n", "spend_thb"),  # more than 2 decimal places
        (b"C9,Name,Email,100.00,10.5,1\n", "lead_count"),  # non-integer
        (b"C9,Name,Email,100.00,-5,1\n", "lead_count"),  # negative
        (b"C9,Name,Email,100.00,10,abc\n", "qualified_lead_count"),
    ],
)
def test_each_field_rule_is_enforced(row, expected_field):
    header = b"campaign_id,campaign_name,channel,spend_thb,lead_count,qualified_lead_count\n"
    parsed = parse_and_validate_csv(header + row)
    assert len(parsed.errors) == 1
    assert parsed.errors[0].field == expected_field


def test_invalid_rows_are_all_reported():
    parsed = parse_and_validate_csv(INVALID_ROWS_CSV)
    assert len(parsed.errors) == 3  # negative spend, qualified>lead, duplicate id
    fields = {e.field for e in parsed.errors}
    assert "spend_thb" in fields
    assert "qualified_lead_count" in fields
    assert "campaign_id" in fields
    codes = {e.application_error_code for e in parsed.errors}
    assert ApplicationErrorCode.DUPLICATE_CAMPAIGN_ID.value in codes
    assert ApplicationErrorCode.INVALID_CSV_ROW.value in codes


def test_import_atomic_no_partial_persistence_on_invalid_file(session_factory):
    session = session_factory()
    try:
        with pytest.raises(ApplicationError):
            import_csv(session, "bad.csv", INVALID_ROWS_CSV)

        from app.models import Campaign, Dataset

        assert session.query(Dataset).count() == 0
        assert session.query(Campaign).count() == 0
    finally:
        session.close()


def test_import_valid_csv_persists_dataset_and_campaigns(session_factory):
    session = session_factory()
    try:
        dataset = import_csv(session, "good.csv", VALID_CSV)
        assert dataset.id is not None
        assert dataset.row_count == 3

        from app.models import Campaign

        assert session.query(Campaign).filter_by(dataset_id=dataset.id).count() == 3
    finally:
        session.close()


def test_api_import_valid_csv_returns_dataset_id(client):
    response = client.post(
        "/api/datasets/import", files={"file": ("valid.csv", VALID_CSV, "text/csv")}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["dataset_id"] > 0
    assert body["row_count"] == 3


def test_api_import_missing_column_returns_422_invalid_schema(client):
    response = client.post(
        "/api/datasets/import", files={"file": ("bad.csv", MISSING_COLUMN_CSV, "text/csv")}
    )
    assert response.status_code == 422
    assert response.json()["application_error_code"] == "INVALID_CSV_SCHEMA"


def test_api_import_invalid_rows_returns_actionable_errors_and_no_partial_import(client):
    response = client.post(
        "/api/datasets/import", files={"file": ("bad.csv", INVALID_ROWS_CSV, "text/csv")}
    )
    assert response.status_code == 422
    body = response.json()
    assert body["application_error_code"] in {"INVALID_CSV_ROW", "DUPLICATE_CAMPAIGN_ID"}
    assert len(body["errors"]) == 3
    for err in body["errors"]:
        assert "row" in err and "field" in err and "message" in err

    # Confirm nothing was persisted: dataset_id=1 should not resolve.
    summary_response = client.get("/api/datasets/1/summary")
    assert summary_response.status_code == 404
