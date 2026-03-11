"""!
@file validation/validator.py
@brief Math accessibility validator.

@details
Validates math expressions for WCAG compliance, semantic structure
completeness, and ARIA attribute correctness.  Usable from the
REST API (``POST /api/v1/validate``), the CLI
(``amr validate <file>``), and as a Python API.

@section validator_usage Usage
@code{.py}
from accessible_math_reader.validation import MathValidator

v = MathValidator()
result = v.validate_expression(r"\\frac{a}{b}")
print(result)
# {
#   "valid": True,
#   "wcag_violations": [],
#   "missing_semantic_structure": [],
#   "aria_warnings": [],
# }
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MathValidator:
    """!
    @brief Validates mathematical expressions for accessibility compliance.

    @details
    Wraps ``AccessibilityContract`` validation methods and adds higher-level
    checks for document-level accessibility, including:
      - WCAG 1.1.1 (Non-text Content): every expression must have alt text
      - WCAG 4.1.2 (Name, Role, Value): ARIA attributes must be correct
      - Semantic completeness: expression must parse to a valid AST
    """

    def validate_expression(self, input_str: str) -> dict[str, Any]:
        """!
        @brief Validate a single math expression.

        @param input_str  LaTeX, MathML, or plaintext math
        @return Dictionary with validation results
        """
        wcag_violations: list[dict[str, str]] = []
        semantic_issues: list[str] = []
        aria_warnings: list[str] = []

        # 1. Try to parse the expression
        try:
            from accessible_math_reader.core.parser import MathParser
            parser = MathParser()
            tree = parser.parse(input_str)
        except Exception as exc:
            wcag_violations.append({
                "rule": "WCAG 4.1.2",
                "description": f"Expression cannot be parsed: {exc}",
                "severity": "error",
            })
            return {
                "valid": False,
                "wcag_violations": wcag_violations,
                "missing_semantic_structure": ["Unparseable expression"],
                "aria_warnings": [],
                "input": input_str,
            }

        # 2. Validate node accessibility via AccessibilityContract
        try:
            from accessible_math_reader.core.accessibility_contract import (
                AccessibilityContract,
            )
            is_valid, issues = AccessibilityContract.validate_node_accessibility(tree)
            if not is_valid:
                for issue in issues:
                    aria_warnings.append(issue)
        except Exception as exc:
            logger.warning(
                "AccessibilityContract validation failed: %s", exc
            )

        # 3. Check semantic structure completeness
        if not tree.children:
            semantic_issues.append(
                "Expression parsed but has no child nodes"
            )

        # 4. Check for speech text availability
        try:
            from accessible_math_reader.speech.rules import SpeechRenderer
            renderer = SpeechRenderer()
            speech = renderer.render(tree)
            if not speech or not speech.strip():
                wcag_violations.append({
                    "rule": "WCAG 1.1.1",
                    "description": "Expression produces empty speech text",
                    "severity": "warning",
                })
        except Exception as exc:
            wcag_violations.append({
                "rule": "WCAG 1.1.1",
                "description": f"Speech generation failed: {exc}",
                "severity": "error",
            })

        valid = (
            len(wcag_violations) == 0
            and len(semantic_issues) == 0
            and len(aria_warnings) == 0
        )

        return {
            "valid": valid,
            "wcag_violations": wcag_violations,
            "missing_semantic_structure": semantic_issues,
            "aria_warnings": aria_warnings,
            "input": input_str,
        }

    def validate_file(
        self,
        path: str | Path,
        fail_on_error: bool = False,
    ) -> dict[str, Any]:
        """!
        @brief Validate all math expressions in a .tex or .txt file.

        @param path           Path to the file
        @param fail_on_error  If True, include "exit_code" in results
        @return Aggregated validation results
        """
        path = Path(path)
        if not path.exists():
            return {
                "valid": False,
                "error": f"File not found: {path}",
                "expressions": [],
            }

        content = path.read_text(encoding="utf-8")

        # Extract math expressions from the file
        expressions = self._extract_expressions(content, path.suffix)

        if not expressions:
            return {
                "valid": True,
                "message": "No math expressions found in file",
                "expressions": [],
                "file": str(path),
            }

        results: list[dict[str, Any]] = []
        any_invalid = False

        for expr in expressions:
            result = self.validate_expression(expr)
            results.append(result)
            if not result["valid"]:
                any_invalid = True

        output: dict[str, Any] = {
            "valid": not any_invalid,
            "file": str(path),
            "total_expressions": len(expressions),
            "valid_count": sum(1 for r in results if r["valid"]),
            "invalid_count": sum(1 for r in results if not r["valid"]),
            "expressions": results,
        }

        if fail_on_error:
            output["exit_code"] = 1 if any_invalid else 0

        return output

    # ── Internal helpers ──────────────────────────────────────────

    @staticmethod
    def _extract_expressions(content: str, suffix: str) -> list[str]:
        """!
        @brief Extract math expressions from file content.

        @details
        For .tex files: extracts from ``$...$``, ``$$...$$``,
        ``\\begin{equation}...\\end{equation}``, etc.
        For other files: treats each non-blank line as an expression.

        @param content  File text content
        @param suffix   File extension (e.g. ".tex")
        @return List of extracted expression strings
        """
        if suffix in (".tex", ".latex"):
            expressions: list[str] = []

            # Display math: $$...$$
            for match in re.finditer(r'\$\$(.+?)\$\$', content, re.DOTALL):
                expressions.append(match.group(1).strip())

            # Inline math: $...$  (exclude $$)
            for match in re.finditer(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', content):
                expressions.append(match.group(1).strip())

            # \begin{equation}...\end{equation}
            for match in re.finditer(
                r'\\begin\{(?:equation|align|gather|math)\*?\}(.+?)'
                r'\\end\{(?:equation|align|gather|math)\*?\}',
                content,
                re.DOTALL,
            ):
                expressions.append(match.group(1).strip())

            return expressions

        # Default: each non-blank line is an expression
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]
