"""!
@file observability/tracing.py
@brief Optional OpenTelemetry tracing integration.

@details
Provides thin wrappers around OpenTelemetry span creation so that
the rest of the codebase can call ``start_span()`` without
importing or checking for OTel availability.

When OpenTelemetry is **not** installed, all functions are safe
no-ops with zero overhead.

Environment variables:
  AMR_TRACING         — "true" to enable (default: false)
  AMR_SERVICE_NAME    — OTEL service name (default: "amr")
  OTEL_EXPORTER_OTLP_ENDPOINT — standard OTel env var

@section tracing_usage Usage
@code{.py}
from accessible_math_reader.observability.tracing import start_span

with start_span("parse_latex") as span:
    span.set_attribute("input.length", len(latex))
    tree = parser.parse(latex)
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator, Optional


# ---------------------------------------------------------------------------
# Try to import OpenTelemetry — entirely optional
# ---------------------------------------------------------------------------

_OTEL_AVAILABLE = False
_tracer: Any = None

try:                                                      # pragma: no cover
    from opentelemetry import trace                       # type: ignore[import-untyped]
    from opentelemetry.sdk.trace import TracerProvider     # type: ignore[import-untyped]
    from opentelemetry.sdk.resources import Resource       # type: ignore[import-untyped]
    _OTEL_AVAILABLE = True
except ImportError:
    pass


def _get_tracer() -> Any:
    """!
    @brief Lazily initialise and return the OTel tracer.

    @details
    Creates a ``TracerProvider`` on first call. Subsequent calls
    return the cached tracer instance.

    @return An OpenTelemetry ``Tracer``, or ``None`` if OTel is
            unavailable or tracing is disabled.
    """
    global _tracer   # noqa: PLW0603 — intentional module-level cache
    if _tracer is not None:
        return _tracer

    enabled = os.environ.get("AMR_TRACING", "false").lower() == "true"
    if not (_OTEL_AVAILABLE and enabled):
        return None

    service_name = os.environ.get("AMR_SERVICE_NAME", "amr")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("accessible_math_reader")
    return _tracer


# ---------------------------------------------------------------------------
# Null-span stub (used when OTel is disabled)
# ---------------------------------------------------------------------------

class _NullSpan:
    """No-op span that silently accepts any attribute or event."""

    def set_attribute(self, key: str, value: Any) -> None:  # noqa: ANN401
        pass

    def add_event(self, name: str, attributes: Optional[dict] = None) -> None:
        pass

    def set_status(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        pass

    def __enter__(self) -> "_NullSpan":
        return self

    def __exit__(self, *exc: Any) -> None:  # noqa: ANN401
        pass


_NULL_SPAN = _NullSpan()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@contextmanager
def start_span(
    name: str,
    attributes: Optional[dict[str, Any]] = None,
) -> Generator[Any, None, None]:
    """!
    @brief Start an OpenTelemetry span (or a no-op if OTel is disabled).

    @param name        Span name (e.g. "parse_latex")
    @param attributes  Optional dict of initial span attributes

    @return Context manager yielding the span (or a silent no-op stub)
    """
    tracer = _get_tracer()
    if tracer is None:
        yield _NullSpan()
        return

    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield span
