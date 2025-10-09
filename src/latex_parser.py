def parse_math_input(expr: str) -> str:
    """Convert LaTeX/MathML to a simplified readable math sentence."""
    replacements = {
        r"\\frac": "fraction",
        r"\\sqrt": "square root",
        r"\\sum": "summation",
        r"\\int": "integral",
        r"\\alpha": "alpha",
        r"\\beta": "beta",
        "^": "to the power of",
        "_": "subscript",
        "=": "equals",
        "+": "plus",
        "-": "minus"
    }
    for k, v in replacements.items():
        expr = expr.replace(k, f" {v} ")
    return expr.strip()
