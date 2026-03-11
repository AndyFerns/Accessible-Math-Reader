"""!
@file api/errors.py
@brief Structured JSON error responses for the REST API.

@details
Provides standardised error response formatting and Flask error
handler registration so that all API errors return consistent JSON.

Response format:
@code{.json}
{
  "error": "Human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "details": {}
}
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

from typing import Any, Optional

from flask import jsonify


# ---------------------------------------------------------------------------
# Error codes
# ---------------------------------------------------------------------------

class ErrorCode:
    """Machine-readable error codes returned in the ``code`` field."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PARSE_ERROR = "PARSE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_INVALID = "AUTH_INVALID"
    RATE_LIMITED = "RATE_LIMITED"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    NOT_FOUND = "NOT_FOUND"


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def error_response(
    message: str,
    code: str,
    status: int = 400,
    details: Optional[dict[str, Any]] = None,
) -> tuple:
    """!
    @brief Build a JSON error response tuple.

    @param message  Human-readable error description
    @param code     Machine-readable error code from ``ErrorCode``
    @param status   HTTP status code (default 400)
    @param details  Optional extra context
    @return (response, status_code) tuple suitable for Flask
    """
    body: dict[str, Any] = {
        "error": message,
        "code": code,
    }
    if details:
        body["details"] = details
    return jsonify(body), status


# ---------------------------------------------------------------------------
# Flask error handler registration
# ---------------------------------------------------------------------------

def register_error_handlers(app_or_bp: Any) -> None:
    """!
    @brief Register JSON error handlers on a Flask app or Blueprint.

    @param app_or_bp  Flask app or Blueprint instance
    """

    @app_or_bp.errorhandler(400)
    def bad_request(exc: Any) -> tuple:
        return error_response(
            str(exc), ErrorCode.VALIDATION_ERROR, 400
        )

    @app_or_bp.errorhandler(404)
    def not_found(exc: Any) -> tuple:
        return error_response(
            "Endpoint not found", ErrorCode.NOT_FOUND, 404
        )

    @app_or_bp.errorhandler(413)
    def payload_too_large(exc: Any) -> tuple:
        return error_response(
            "Request payload exceeds size limit",
            ErrorCode.PAYLOAD_TOO_LARGE,
            413,
        )

    @app_or_bp.errorhandler(429)
    def rate_limited(exc: Any) -> tuple:
        return error_response(
            "Rate limit exceeded — please retry later",
            ErrorCode.RATE_LIMITED,
            429,
        )

    @app_or_bp.errorhandler(500)
    def internal_error(exc: Any) -> tuple:
        return error_response(
            "Internal server error",
            ErrorCode.INTERNAL_ERROR,
            500,
        )
