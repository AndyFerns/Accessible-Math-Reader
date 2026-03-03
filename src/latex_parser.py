import re
import xml.etree.ElementTree as ET

def parse_mathml(mathml_str):
    """
    Parse MathML input and convert it into a readable English string.
    Example: <math><mfrac><mi>a</mi><mi>b</mi></mfrac></math> -> 'a divided by b'
    """
    try:
        root = ET.fromstring(mathml_str)
    except ET.ParseError:
        return "Invalid MathML syntax."

    def walk(node):
        tag = node.tag.split('}')[-1]  # remove namespace if present

        if tag == "math":
            return " ".join(walk(child) for child in node)
        elif tag == "mfrac":
            if len(list(node)) == 2:
                num, denom = list(node)
                return f"{walk(num)} divided by {walk(denom)}"
        elif tag == "msup":
            if len(list(node)) == 2:
                base, exp = list(node)
                return f"{walk(base)} to the power of {walk(exp)}"
        elif tag == "msub":
            if len(list(node)) == 2:
                base, sub = list(node)
                return f"{walk(base)} sub {walk(sub)}"
        elif tag == "msqrt":
            if len(list(node)) == 1:
                return f"square root of {walk(node[0])}"
        elif tag == "mi" or tag == "mn":
            return node.text.strip() if node.text else ""
        elif tag == "mo":
            ops = {"+": "plus", "-": "minus", "=": "equals", "*": "times", "(": "", ")": ""}
            return ops.get(node.text.strip(), node.text.strip())
        
        # Fallback for other tags
        return " ".join(walk(child) for child in node)

    return walk(root)


def parse_latex(latex_str):
    """
    Parse basic LaTeX input and convert it into a readable English string.
    This version handles more common cases like exponents, subscripts, and Greek letters.
    """
    text = latex_str.strip()

    # 1. Handle Greek letters and special symbols first
    symbol_map = {
        '\\pi': 'pi', '\\alpha': 'alpha', '\\beta': 'beta', '\\gamma': 'gamma',
        '\\delta': 'delta', '\\epsilon': 'epsilon', '\\theta': 'theta',
        '\\infty': 'infinity', '\\pm': 'plus or minus', '\\times': 'times',
        '\\cdot': 'times', '\\div': 'divided by', '\\leq': 'less than or equal to',
        '\\geq': 'greater than or equal to', '\\neq': 'not equal to',
    }
    for key, value in symbol_map.items():
        text = text.replace(key, value)

    # 2. Use regex for structural replacements (order is important)
    # Using a list of tuples to control the order of operations
    structural_replacements = [
        # Exponents: x^{...} or x^y
        (r'([a-zA-Z0-9]+)\^\{(.+?)\}', r'\1 to the power of (\2)'),
        (r'([a-zA-Z0-9]+)\^([a-zA-Z0-9]+)', r'\1 to the power of \2'),
        # Subscripts: H_{...} or H_2
        (r'([a-zA-Z0-9]+)_\{(.+?)\}', r'\1 sub (\2)'),
        (r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', r'\1 sub \2'),
        # Fractions
        (r'\\frac{(.+?)}{(.+?)}', r'(\1) divided by (\2)'),
        # Square roots
        (r'\\sqrt{(.+?)}', r'square root of (\1)'),
        # Keywords
        (r'\\sum', 'summation of'),
        (r'\\int', 'integral of'),
    ]
    # Iteratively apply replacements
    for pattern, repl in structural_replacements:
        text = re.sub(pattern, repl, text)
    # Re-run for nested cases (e.g., \frac{a^2}{b})
    for pattern, repl in structural_replacements:
        text = re.sub(pattern, repl, text)

    # 3. Clean up remaining symbols and characters
    cleanup_map = {
        '{': '(', '}': ')',
        '+': ' plus ', '-': ' minus ', '=': ' equals ',
        '*': ' times ', '/': ' divided by ',
        '<': ' less than ', '>': ' greater than ',
        '$': '',  # Remove math delimiters
        '\\': '' # Remove any remaining backslashes
    }
    for key, value in cleanup_map.items():
        text = text.replace(key, value)

    # 4. Normalize whitespace to a single space
    return ' '.join(text.split())


# --- NEW FUNCTION ---
def latex_to_braille_simple(input_str):
    """
    Convert LaTeX, MathML, or plaintext to a simple char string
    that braille_converter.py can understand.

    Examples:
        \frac{a}{b}  -> (a)/(b)
        a^2          -> a2
        b_i          -> bi
        x² + y²      -> x2+y2
        (a+b)/(c-d)  -> (a+b)/(c-d)
    """
    stripped = input_str.strip()

    # MathML branch – no change from original behaviour
    if stripped.startswith("<math"):
        return "MathML(Braille-TBD)"

    # Detect whether the input is LaTeX or plaintext.
    # LaTeX is recognised by the presence of backslash commands.
    import re as _re
    is_latex = bool(_re.search(r"\\[a-zA-Z]+", stripped))

    if is_latex:
        text = stripped
        # Original LaTeX → simple-string replacements
        replacements = [
            (r'\\frac{(.+?)}{(.+?)}', r'(\1)/(\2)'),
            (r'([a-zA-Z0-9]+)\^\{?(.+?)\}?', r'\1\2'),
            (r'([a-zA-Z0-9]+)_\{?(.+?)\}?', r'\1\2'),
            (r'\\pm', '+'),
            (r'\\times', '*'),
            (r'\\cdot', '*'),
            (r'\\div', '/'),
            (r'[$]', ''), (r'[\\{}]', ''),
            (r'\\sqrt', ''),
        ]
        for pattern, repl in replacements:
            text = _re.sub(pattern, repl, text)
        return text.replace(' ', '')

    # Plaintext / Unicode branch -------------------------------------------
    # Strip Unicode super/subscript digits into their ASCII equivalents,
    # map common Unicode symbols, and remove whitespace.
    _sup_map = {
        '\u2070': '0', '\u00b9': '1', '\u00b2': '2', '\u00b3': '3',
        '\u2074': '4', '\u2075': '5', '\u2076': '6', '\u2077': '7',
        '\u2078': '8', '\u2079': '9',
    }
    _sub_map = {
        '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3',
        '\u2084': '4', '\u2085': '5', '\u2086': '6', '\u2087': '7',
        '\u2088': '8', '\u2089': '9',
    }
    _sym_map = {
        '\u00d7': '*', '\u00b7': '*', '\u22c5': '*',
        '\u00f7': '/', '\u00b1': '+', '\u221a': '',
        '\u03c0': 'pi', '\u221e': 'inf',
        '\u2264': '<', '\u2265': '>', '\u2260': '!=',
    }
    text = stripped
    for src, dst in {**_sup_map, **_sub_map, **_sym_map}.items():
        text = text.replace(src, dst)
    # Replace ** with nothing (already handled by removing the operator)
    text = text.replace('**', '')
    return text.replace(' ', '')


def _parse_plaintext(text):
    """
    Parse a plaintext / Unicode math expression into readable English.

    This handles everyday copy-paste formats such as:
        (a+b)/(c-d)   -> (a plus b) divided by (c minus d)
        x^2           -> x to the power of 2
        x**2          -> x to the power of 2
        sqrt(x)       -> square root of x
        x² + y²       -> x to the power of 2 plus y to the power of 2
        π             -> pi
        ≤  ≥  ≠       -> less than or equal to / greater than or equal to / not equal to
    """
    import re as _re

    # 1. Map Unicode symbols to words
    _symbol_words = {
        'π': 'pi', 'α': 'alpha', 'β': 'beta', 'γ': 'gamma',
        'δ': 'delta', 'ε': 'epsilon', 'θ': 'theta', 'λ': 'lambda',
        'σ': 'sigma', 'ω': 'omega', 'Σ': 'summation of',
        '∫': 'integral of', '∞': 'infinity',
        '±': 'plus or minus', '×': 'times', '·': 'times',
        '÷': 'divided by', '√': 'square root of',
        '≤': 'less than or equal to', '≥': 'greater than or equal to',
        '≠': 'not equal to', '≈': 'approximately equal to',
    }
    for src, dst in _symbol_words.items():
        text = text.replace(src, f' {dst} ')

    # 2. Unicode superscript digits -> "to the power of N"
    _sup_map = {
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
        '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    }
    sup_pat = '[' + ''.join(_sup_map.keys()) + ']+'
    def _sup_repl(m):
        digits = ''.join(_sup_map[c] for c in m.group())
        return f' to the power of {digits}'
    text = _re.sub(sup_pat, _sup_repl, text)

    # 3. Unicode subscript digits -> "sub N"
    _sub_map = {
        '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
        '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    }
    sub_pat = '[' + ''.join(_sub_map.keys()) + ']+'
    def _sub_repl(m):
        digits = ''.join(_sub_map[c] for c in m.group())
        return f' sub {digits}'
    text = _re.sub(sub_pat, _sub_repl, text)

    # 4. Structural patterns (order matters)
    structural = [
        # sqrt(...)  -> square root of (...)
        (r'sqrt\((.+?)\)', r'square root of (\1)'),
        # Exponents: x^{...} or x^y  or x**y
        (r'([a-zA-Z0-9]+)\*\*\{(.+?)\}', r'\1 to the power of (\2)'),
        (r'([a-zA-Z0-9]+)\*\*([a-zA-Z0-9]+)', r'\1 to the power of \2'),
        (r'([a-zA-Z0-9]+)\^\{(.+?)\}', r'\1 to the power of (\2)'),
        (r'([a-zA-Z0-9]+)\^([a-zA-Z0-9]+)', r'\1 to the power of \2'),
        # Subscripts: H_{...} or H_2
        (r'([a-zA-Z0-9]+)_\{(.+?)\}', r'\1 sub (\2)'),
        (r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)', r'\1 sub \2'),
    ]
    for pattern, repl in structural:
        text = _re.sub(pattern, repl, text)
    # Second pass for nested cases
    for pattern, repl in structural:
        text = _re.sub(pattern, repl, text)

    # 5. Operator words
    _ops = {
        '+': ' plus ', '-': ' minus ', '=': ' equals ',
        '*': ' times ', '/': ' divided by ',
        '<': ' less than ', '>': ' greater than ',
    }
    for src, dst in _ops.items():
        text = text.replace(src, dst)

    # 6. Clean up braces and normalise whitespace
    text = text.replace('{', '(').replace('}', ')')
    return ' '.join(text.split())


def parse_math_input(math_str):
    """
    Detect whether input is LaTeX, MathML, or plaintext and return
    readable English text suitable for speech output.

    Detection heuristics (applied in order):
      1. Starts with '<math' -> MathML
      2. Contains LaTeX commands (e.g. \\frac, \\sqrt) -> LaTeX
      3. Everything else -> plaintext / Unicode math
    """
    import re as _re
    stripped = math_str.strip()
    if stripped.startswith("<math"):
        return parse_mathml(stripped)
    if _re.search(r"\\[a-zA-Z]+", stripped):
        return parse_latex(stripped)
    return _parse_plaintext(stripped)