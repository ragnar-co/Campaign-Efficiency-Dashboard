"""Application error codes and HTTP mapping.

`application_error_code` enum owner: API_SPEC.md. Do not add values here that
are not already listed in that document.
"""

from __future__ import annotations

from enum import Enum


class ApplicationErrorCode(str, Enum):
    INVALID_CSV_SCHEMA = "INVALID_CSV_SCHEMA"
    INVALID_CSV_ROW = "INVALID_CSV_ROW"
    DUPLICATE_CAMPAIGN_ID = "DUPLICATE_CAMPAIGN_ID"
    DATASET_NOT_FOUND = "DATASET_NOT_FOUND"
    AI_NOT_CONFIGURED = "AI_NOT_CONFIGURED"
    AI_UPSTREAM_ERROR = "AI_UPSTREAM_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# HTTP mapping per API_SPEC.md: "validation errors -> 400/422; missing dataset
# -> 404; AI configuration/upstream failure -> 503; unexpected server error -> 500"
HTTP_STATUS_BY_CODE: dict[ApplicationErrorCode, int] = {
    ApplicationErrorCode.INVALID_CSV_SCHEMA: 422,
    ApplicationErrorCode.INVALID_CSV_ROW: 422,
    ApplicationErrorCode.DUPLICATE_CAMPAIGN_ID: 422,
    ApplicationErrorCode.DATASET_NOT_FOUND: 404,
    ApplicationErrorCode.AI_NOT_CONFIGURED: 503,
    ApplicationErrorCode.AI_UPSTREAM_ERROR: 503,
    ApplicationErrorCode.INTERNAL_ERROR: 500,
}


class ApplicationError(Exception):
    def __init__(
        self,
        code: ApplicationErrorCode,
        message: str,
        errors: list[dict] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.errors = errors or []

    @property
    def http_status(self) -> int:
        return HTTP_STATUS_BY_CODE[self.code]

    def to_payload(self) -> dict:
        payload: dict = {
            "application_error_code": self.code.value,
            "message": self.message,
        }
        if self.errors:
            payload["errors"] = self.errors
        return payload
