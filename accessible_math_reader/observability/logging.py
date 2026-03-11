"""!
@file observability/logging.py
@brief Structured logging configuration for Accessible Math Reader.

@details
Provides a ``setup_logging()`` helper that configures the Python
logging subsystem for either plain text or JSON output.  JSON mode
is recommended for production / container deployments where log
aggregators (ELK, Loki, CloudWatch) are in use.

Environment variables:
  AMR_LOG_FORMAT  — "json" for structured JSON, anything else for
                    the default human-readable text format.
  AMR_LOG_LEVEL   — Standard Python level name (DEBUG, INFO, …).
                    Defaults to INFO.

@section logging_usage Usage
@code{.py}
from accessible_math_reader.observability.logging import setup_logging

setup_logging()                       # reads env vars
setup_logging(fmt="json", level="DEBUG")  # explicit override
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# JSON Formatter
# ---------------------------------------------------------------------------

class _JSONFormatter(logging.Formatter):
    """!
    @brief Formats log records as single-line JSON objects.

    @details
    Each log line becomes a JSON object with keys:
      timestamp, level, logger, message, module, funcName, lineno
    Extra fields attached to the record (e.g. via ``extra={…}``)
    are merged into the top level.
    """

    def format(self, record: logging.LogRecord) -> str:
        """!
        @brief Serialize a LogRecord to a JSON string.

        @param record  Python LogRecord
        @return Single-line JSON string (no trailing newline)
        """
        payload: dict = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }

        # Merge any extra fields the caller attached
        # (skip internal LogRecord attributes)
        _RESERVED = logging.LogRecord(
            "", 0, "", 0, "", (), None
        ).__dict__.keys()
        for key, value in record.__dict__.items():
            if key not in _RESERVED and key not in payload:
                payload[key] = value

        # Include exception info when present
        if record.exc_info and record.exc_info[1] is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_logging(
    fmt: Optional[str] = None,
    level: Optional[str] = None,
) -> None:
    """!
    @brief Configure application-wide logging.

    @details
    Safe to call multiple times — removes any existing handlers on the
    root logger before attaching a new one.

    @param fmt    "json" for structured JSON output, or None / anything
                  else for human-readable text.  Falls back to the
                  ``AMR_LOG_FORMAT`` environment variable.
    @param level  Python log level name (e.g. "DEBUG").  Falls back to
                  ``AMR_LOG_LEVEL``, then to INFO.
    """
    # Resolve from env if not supplied
    fmt = fmt or os.environ.get("AMR_LOG_FORMAT", "text")
    level = level or os.environ.get("AMR_LOG_LEVEL", "INFO")

    # Convert level string to int
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove existing handlers to allow reconfiguration
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Create new handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    if fmt.lower() == "json":
        handler.setFormatter(_JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))

    root.addHandler(handler)

    # Quieten noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
