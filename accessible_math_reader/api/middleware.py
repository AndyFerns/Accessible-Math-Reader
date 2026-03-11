"""!
@file api/middleware.py
@brief Optional authentication and rate-limiting middleware.

@details
Provides two Flask decorators that can be applied to API endpoints:
  - ``require_api_key`` — checks ``X-API-Key`` header against a
    configured list of valid keys.
  - ``rate_limit``      — enforces a per-IP sliding-window request
    limit using an in-memory store (no Redis required).

Both are **disabled by default** and controlled via environment
variables.  Self-hosted users should leave ``AMR_ENABLE_AUTH`` and
``AMR_ENABLE_RATE_LIMIT`` as ``false`` for zero overhead.

Environment variables:
  AMR_ENABLE_AUTH     — "true" to require API keys (default: false)
  AMR_API_KEYS        — comma-separated list of valid keys
  AMR_ENABLE_RATE_LIMIT — "true" to enable (default: false)
  AMR_RATE_LIMIT      — "<count>/<period>" e.g. "100/minute" (default)

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import functools
import os
import time
from collections import defaultdict
from threading import Lock
from typing import Any, Callable

from flask import request

from accessible_math_reader.api.errors import ErrorCode, error_response


# ═══════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════

def _auth_enabled() -> bool:
    """Check if API-key authentication is turned on."""
    return os.environ.get("AMR_ENABLE_AUTH", "false").lower() == "true"


def _valid_keys() -> set[str]:
    """Parse the comma-separated list of valid API keys."""
    raw = os.environ.get("AMR_API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


def require_api_key(fn: Callable) -> Callable:
    """!
    @brief Decorator: reject requests missing a valid ``X-API-Key`` header.

    @details
    When ``AMR_ENABLE_AUTH=true``, every decorated endpoint requires
    the header ``X-API-Key: <key>`` where ``<key>`` is one of the
    values in the ``AMR_API_KEYS`` environment variable.

    When authentication is disabled (the default), this decorator
    is a transparent pass-through.
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not _auth_enabled():
            return fn(*args, **kwargs)

        key = request.headers.get("X-API-Key", "")
        keys = _valid_keys()
        if not keys:
            # No keys configured — treat as misconfiguration, deny all
            return error_response(
                "Authentication is enabled but no API keys are configured",
                ErrorCode.INTERNAL_ERROR,
                500,
            )
        if key not in keys:
            return error_response(
                "Missing or invalid API key",
                ErrorCode.AUTH_INVALID,
                401,
            )
        return fn(*args, **kwargs)

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════
# Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════

# In-memory sliding window — per IP
_rate_lock = Lock()
_rate_store: dict[str, list[float]] = defaultdict(list)


def _parse_rate_limit() -> tuple[int, float]:
    """!
    @brief Parse ``AMR_RATE_LIMIT`` into (count, window_seconds).

    @details
    Accepted formats:
      - "100/minute"  →  (100, 60)
      - "1000/hour"   →  (1000, 3600)
      - "10/second"   →  (10, 1)

    Defaults to 100/minute.

    @return Tuple of (max_requests, window_in_seconds)
    """
    raw = os.environ.get("AMR_RATE_LIMIT", "100/minute")
    try:
        count_str, period = raw.strip().split("/")
        count = int(count_str)
    except (ValueError, IndexError):
        return 100, 60.0

    period_map = {
        "second": 1.0,
        "minute": 60.0,
        "hour": 3600.0,
        "day": 86400.0,
    }
    window = period_map.get(period.lower(), 60.0)
    return count, window


def rate_limit(fn: Callable) -> Callable:
    """!
    @brief Decorator: enforce per-IP request rate limiting.

    @details
    Uses an in-memory sliding window.  When ``AMR_ENABLE_RATE_LIMIT``
    is ``false`` (the default), this decorator is a transparent
    pass-through.

    The limit is configured via ``AMR_RATE_LIMIT`` (e.g. "100/minute").
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if os.environ.get(
            "AMR_ENABLE_RATE_LIMIT", "false"
        ).lower() != "true":
            return fn(*args, **kwargs)

        ip = request.remote_addr or "unknown"
        max_requests, window = _parse_rate_limit()
        now = time.time()
        cutoff = now - window

        with _rate_lock:
            # Prune old entries
            _rate_store[ip] = [
                t for t in _rate_store[ip] if t > cutoff
            ]
            if len(_rate_store[ip]) >= max_requests:
                return error_response(
                    "Rate limit exceeded — please retry later",
                    ErrorCode.RATE_LIMITED,
                    429,
                )
            _rate_store[ip].append(now)

        return fn(*args, **kwargs)

    return wrapper
