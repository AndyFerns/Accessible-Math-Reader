"""!
@file api/schemas.py
@brief Request/response validation for the REST API.

@details
Pure-Python validation (no Pydantic dependency).  Provides
``validate_math_request()`` for incoming JSON and response builder
helpers for each endpoint type.

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

from typing import Any, Optional

# Maximum input length (characters) to prevent abuse
MAX_INPUT_LENGTH = 50_000

# Accepted format hints
VALID_FORMATS = {"auto", "latex", "mathml", "plaintext"}

# Accepted Braille notations
VALID_NOTATIONS = {"nemeth", "ueb"}

# Accepted verbosity levels
VALID_VERBOSITIES = {"verbose", "concise", "superbrief"}


# ---------------------------------------------------------------------------
# Request validation
# ---------------------------------------------------------------------------

def validate_math_request(data: Any) -> tuple[Optional[str], Optional[dict]]:
    """!
    @brief Validate an incoming math conversion request body.

    @param data  Parsed JSON body (should be a dict)
    @return (error_message, validated_params)
            — error_message is None on success
            — validated_params is None on failure
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object", None

    input_str = data.get("input")
    if not input_str or not isinstance(input_str, str):
        return "Field 'input' is required and must be a non-empty string", None

    if len(input_str) > MAX_INPUT_LENGTH:
        return (
            f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters",
            None,
        )

    fmt = data.get("format", "auto")
    if fmt not in VALID_FORMATS:
        return (
            f"Invalid format '{fmt}'. Must be one of: {', '.join(sorted(VALID_FORMATS))}",
            None,
        )

    notation = data.get("notation", "nemeth")
    if notation not in VALID_NOTATIONS:
        return (
            f"Invalid notation '{notation}'. Must be one of: {', '.join(sorted(VALID_NOTATIONS))}",
            None,
        )

    verbosity = data.get("verbosity", "verbose")
    if verbosity not in VALID_VERBOSITIES:
        return (
            f"Invalid verbosity '{verbosity}'. Must be one of: {', '.join(sorted(VALID_VERBOSITIES))}",
            None,
        )

    validated = {
        "input": input_str.strip(),
        "format": fmt,
        "notation": notation,
        "verbosity": verbosity,
    }
    return None, validated


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------

def speech_response(text: str, input_str: str) -> dict[str, Any]:
    """Build the JSON body for /api/v1/speech."""
    return {"speech": text, "input": input_str}


def braille_response(
    text: str, notation: str, input_str: str
) -> dict[str, Any]:
    """Build the JSON body for /api/v1/braille."""
    return {"braille": text, "notation": notation, "input": input_str}


def structure_response(
    structure: dict, input_str: str
) -> dict[str, Any]:
    """Build the JSON body for /api/v1/structure."""
    return {"structure": structure, "input": input_str}


def validation_response(results: dict) -> dict[str, Any]:
    """Build the JSON body for /api/v1/validate."""
    return results
