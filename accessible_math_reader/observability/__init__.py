"""!
@file observability/__init__.py
@brief Observability subsystem for Accessible Math Reader.

@details
Provides optional structured logging, Prometheus metrics, and
OpenTelemetry tracing integration.  All components are opt-in
and have zero overhead when disabled.

Configuration via environment variables:
  AMR_LOG_FORMAT   = json | text   (default: text)
  AMR_LOG_LEVEL    = DEBUG | INFO | WARNING | ERROR  (default: INFO)
  AMR_METRICS      = true | false  (default: false)
  AMR_TRACING      = true | false  (default: false)

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from accessible_math_reader.observability.logging import setup_logging
from accessible_math_reader.observability.metrics import MetricsCollector

__all__ = ["setup_logging", "MetricsCollector"]
