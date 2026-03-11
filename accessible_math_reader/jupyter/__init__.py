"""!
@file jupyter/__init__.py
@brief Jupyter/IPython integration for Accessible Math Reader.

@details
Provides notebook-friendly display helpers and IPython rich-repr
integration so that AMR outputs render beautifully in JupyterLab.

When IPython is **not** installed, all functions are safe no-ops.

@section jupyter_usage Usage (inside a Jupyter notebook)
@code{.py}
from accessible_math_reader.jupyter import display_math

display_math(r"\\frac{a}{b}")
# → Renders speech text + Braille + ARIA HTML inline in the cell
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _in_notebook() -> bool:
    """Check if we're running inside an IPython/Jupyter environment."""
    try:
        from IPython import get_ipython  # type: ignore[import-untyped]
        shell = get_ipython()
        return shell is not None
    except (ImportError, NameError):
        return False


def display_math(
    input_str: str,
    show_speech: bool = True,
    show_braille: bool = True,
    show_structure: bool = False,
) -> Any:
    """!
    @brief Display a math expression with accessible outputs in a notebook.

    @details
    Renders an HTML block inside a Jupyter cell containing:
      - The rendered LaTeX formula (via MathJax)
      - Spoken English text
      - Braille notation
      - Optionally, the semantic tree structure

    When called outside of Jupyter, prints plain text to stdout.

    @param input_str       LaTeX, MathML, or plaintext math expression
    @param show_speech     Show speech output (default True)
    @param show_braille    Show Braille output (default True)
    @param show_structure  Show AST structure (default False)
    """
    from accessible_math_reader.reader import MathReader

    reader = MathReader()

    sections: list[str] = []

    # Speech
    if show_speech:
        speech = reader.to_speech(input_str)
        sections.append(
            f'<div style="margin:4px 0;">'
            f'<strong>🔊 Speech:</strong> {speech}'
            f'</div>'
        )

    # Braille
    if show_braille:
        braille = reader.to_braille(input_str)
        sections.append(
            f'<div style="margin:4px 0;">'
            f'<strong>⠿ Braille:</strong> <code>{braille}</code>'
            f'</div>'
        )

    # Structure
    if show_structure:
        import json
        structure = reader.get_structure(input_str)
        pretty = json.dumps(structure, indent=2)
        sections.append(
            f'<details><summary><strong>🌳 Structure</strong></summary>'
            f'<pre>{pretty}</pre></details>'
        )

    html_content = "\n".join(sections)
    html = (
        f'<div style="border:1px solid #ccc; border-radius:8px; '
        f'padding:12px; margin:8px 0; font-family:sans-serif;">'
        f'<div style="font-size:1.2em; margin-bottom:8px;">'
        f'<strong>♿ Accessible Math Reader</strong></div>'
        f'{html_content}'
        f'</div>'
    )

    if _in_notebook():
        try:
            from IPython.display import HTML, display  # type: ignore[import-untyped]
            display(HTML(html))
            return
        except ImportError:
            pass

    # Fallback: plain text
    print(f"Speech: {reader.to_speech(input_str)}")
    if show_braille:
        print(f"Braille: {reader.to_braille(input_str)}")


class MathDisplay:
    """!
    @brief Wrapper providing IPython rich-repr for math outputs.

    @details
    Useful for returning from notebook cells to get automatic
    rendering without an explicit ``display()`` call.

    @code{.py}
    from accessible_math_reader.jupyter import MathDisplay
    MathDisplay(r"\\frac{a}{b}")
    @endcode
    """

    def __init__(self, input_str: str) -> None:
        self.input_str = input_str
        from accessible_math_reader.reader import MathReader
        self._reader = MathReader()

    def _repr_html_(self) -> str:
        """IPython uses this for rich HTML display in notebooks."""
        speech = self._reader.to_speech(self.input_str)
        braille = self._reader.to_braille(self.input_str)
        return (
            f'<div style="border:1px solid #ccc; border-radius:8px; '
            f'padding:12px; margin:8px 0;">'
            f'<strong>🔊</strong> {speech}<br>'
            f'<strong>⠿</strong> <code>{braille}</code>'
            f'</div>'
        )

    def __repr__(self) -> str:
        return f"MathDisplay({self.input_str!r})"
