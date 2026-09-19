from datetime import date
from decimal import Decimal, InvalidOperation

from flask import request

from .errors import ApiError


def json_body() -> dict:
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError("A JSON request body is required")
    return body


def required_text(body: dict, field: str, *, max_length: int | None = None) -> str:
    value = body.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ApiError(f"{field} is required", details={field: "Required"})
    value = value.strip()
    if max_length and len(value) > max_length:
        raise ApiError(
            f"{field} is too long",
            details={field: f"Maximum length is {max_length}"},
        )
    return value


def optional_text(
    body: dict, field: str, *, max_length: int | None = None
) -> str | None:
    value = body.get(field)
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ApiError(f"{field} must be text", details={field: "Invalid text"})
    value = value.strip()
    if max_length and len(value) > max_length:
        raise ApiError(
            f"{field} is too long",
            details={field: f"Maximum length is {max_length}"},
        )
    return value


def parse_date(value, field: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ApiError(
            f"{field} must use YYYY-MM-DD format",
            details={field: "Invalid date"},
        ) from exc


def parse_int(value, field: str, *, minimum: int, maximum: int | None = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(
            f"{field} must be a number", details={field: "Invalid number"}
        ) from exc
    if parsed < minimum or (maximum is not None and parsed > maximum):
        range_text = (
            f"between {minimum} and {maximum}" if maximum else f"at least {minimum}"
        )
        raise ApiError(f"{field} must be {range_text}", details={field: "Out of range"})
    return parsed


def parse_decimal(value, field: str, *, minimum: Decimal = Decimal("0.01")) -> Decimal:
    try:
        parsed = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ApiError(
            f"{field} must be a valid amount", details={field: "Invalid amount"}
        ) from exc
    if parsed < minimum:
        raise ApiError(
            f"{field} must be at least {minimum}", details={field: "Out of range"}
        )
    return parsed
