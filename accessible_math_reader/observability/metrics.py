"""!
@file observability/metrics.py
@brief Prometheus-compatible metrics for Accessible Math Reader.

@details
Provides a lightweight ``MetricsCollector`` that tracks request counts,
parse durations, and error totals.  When the optional ``prometheus_client``
library is installed, metrics are exposed in Prometheus text format via
``MetricsCollector.render()``.

If ``prometheus_client`` is **not** installed, the collector degrades
gracefully to in-memory counters accessible through ``snapshot()``.

Environment variables:
  AMR_METRICS  — set to "true" to enable collection (default: false)

@section metrics_usage Usage
@code{.py}
from accessible_math_reader.observability.metrics import MetricsCollector

mc = MetricsCollector()
mc.inc_request("speech")
mc.observe_duration("parse", 0.042)
mc.inc_error("parse_error")

# Prometheus text exposition
print(mc.render())

# Raw snapshot (always available, even without prometheus_client)
print(mc.snapshot())
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from contextlib import contextmanager
from threading import Lock
from typing import Any, Generator, Optional


# ---------------------------------------------------------------------------
# Prometheus integration (optional)
# ---------------------------------------------------------------------------

_PROM_AVAILABLE = False
try:                                         # pragma: no cover
    import prometheus_client                 # type: ignore[import-untyped]
    _PROM_AVAILABLE = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MetricsCollector:
    """!
    @brief Collects and exposes operational metrics.

    @details
    Thread-safe.  Wraps ``prometheus_client`` when available, otherwise
    stores counters in a plain dictionary.

    Metrics tracked:
      - ``amr_requests_total{endpoint}``          — request counter
      - ``amr_parse_duration_seconds{operation}``  — histogram / timer
      - ``amr_errors_total{error_type}``           — error counter
    """

    # ── Construction ──────────────────────────────────────────────

    def __init__(self, enabled: Optional[bool] = None) -> None:
        """!
        @brief Initialise the metrics collector.

        @param enabled  Override for enable/disable.  If ``None``,
                        reads the ``AMR_METRICS`` env var (default false).
        """
        if enabled is None:
            enabled = os.environ.get("AMR_METRICS", "false").lower() == "true"
        self._enabled = enabled

        # In-memory fallback counters (always maintained)
        self._lock = Lock()
        self._counters: dict[str, dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self._durations: dict[str, list[float]] = defaultdict(list)

        # Prometheus objects (created only when library is available)
        self._prom_requests: Any = None
        self._prom_errors: Any = None
        self._prom_duration: Any = None
        if _PROM_AVAILABLE and self._enabled:
            self._prom_requests = prometheus_client.Counter(
                "amr_requests_total",
                "Total API requests",
                ["endpoint"],
            )
            self._prom_errors = prometheus_client.Counter(
                "amr_errors_total",
                "Total errors",
                ["error_type"],
            )
            self._prom_duration = prometheus_client.Histogram(
                "amr_parse_duration_seconds",
                "Operation duration in seconds",
                ["operation"],
                buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
            )

    # ── Recording ─────────────────────────────────────────────────

    def inc_request(self, endpoint: str, amount: float = 1) -> None:
        """!
        @brief Increment the request counter for an endpoint.

        @param endpoint  Endpoint label (e.g. "speech", "braille")
        @param amount    Increment value (default 1)
        """
        if not self._enabled:
            return
        with self._lock:
            self._counters["requests"][endpoint] += amount
        if self._prom_requests is not None:
            self._prom_requests.labels(endpoint=endpoint).inc(amount)

    def inc_error(self, error_type: str, amount: float = 1) -> None:
        """!
        @brief Increment the error counter.

        @param error_type  Error label (e.g. "parse_error", "tts_error")
        @param amount      Increment value (default 1)
        """
        if not self._enabled:
            return
        with self._lock:
            self._counters["errors"][error_type] += amount
        if self._prom_errors is not None:
            self._prom_errors.labels(error_type=error_type).inc(amount)

    def observe_duration(self, operation: str, seconds: float) -> None:
        """!
        @brief Record an operation duration.

        @param operation  Operation label (e.g. "parse", "render")
        @param seconds    Duration in seconds
        """
        if not self._enabled:
            return
        with self._lock:
            self._durations[operation].append(seconds)
        if self._prom_duration is not None:
            self._prom_duration.labels(operation=operation).observe(seconds)

    @contextmanager
    def timer(self, operation: str) -> Generator[None, None, None]:
        """!
        @brief Context manager that measures and records elapsed time.

        @param operation  Operation label

        @section timer_usage Example
        @code{.py}
        with mc.timer("parse"):
            tree = parser.parse(input_str)
        @endcode
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.observe_duration(operation, elapsed)

    # ── Exposition ────────────────────────────────────────────────

    def render(self) -> str:
        """!
        @brief Render metrics in Prometheus text exposition format.

        @details
        Uses ``prometheus_client.generate_latest()`` when available.
        Falls back to a simple text rendering of internal counters.

        @return Prometheus-compatible text
        """
        if _PROM_AVAILABLE and self._enabled:
            return prometheus_client.generate_latest().decode("utf-8")
        # Fallback: simple text format
        return self._render_fallback()

    def snapshot(self) -> dict[str, Any]:
        """!
        @brief Return a plain-dict snapshot of all collected metrics.

        @return Dictionary with "requests", "errors", and "durations" keys
        """
        with self._lock:
            return {
                "requests": dict(self._counters["requests"]),
                "errors": dict(self._counters["errors"]),
                "durations": {
                    op: {
                        "count": len(vals),
                        "total_seconds": sum(vals),
                        "avg_seconds": sum(vals) / len(vals) if vals else 0,
                    }
                    for op, vals in self._durations.items()
                },
            }

    # ── Internals ─────────────────────────────────────────────────

    def _render_fallback(self) -> str:
        """Render a minimal Prometheus-compatible text without the library."""
        lines: list[str] = []
        with self._lock:
            for endpoint, count in self._counters["requests"].items():
                lines.append(
                    f'amr_requests_total{{endpoint="{endpoint}"}} {count}'
                )
            for error_type, count in self._counters["errors"].items():
                lines.append(
                    f'amr_errors_total{{error_type="{error_type}"}} {count}'
                )
            for op, vals in self._durations.items():
                lines.append(
                    f'amr_parse_duration_seconds_count{{operation="{op}"}} '
                    f"{len(vals)}"
                )
                lines.append(
                    f'amr_parse_duration_seconds_sum{{operation="{op}"}} '
                    f"{sum(vals):.6f}"
                )
        return "\n".join(lines) + "\n" if lines else ""
