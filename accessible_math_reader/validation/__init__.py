"""!
@file validation/__init__.py
@brief Accessibility validation subsystem.

@details
Provides ``MathValidator`` for checking mathematical expressions
against WCAG and ARIA accessibility standards.

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from accessible_math_reader.validation.validator import MathValidator

__all__ = ["MathValidator"]
