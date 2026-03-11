"""!
@file api/__init__.py
@brief REST API subsystem for Accessible Math Reader.

@details
Provides a versioned REST API (``/api/v1/``) as a Flask Blueprint
that can be registered on any Flask application.  Includes optional
authentication, rate limiting, and Prometheus metrics.

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from accessible_math_reader.api.app import create_api_blueprint

__all__ = ["create_api_blueprint"]
