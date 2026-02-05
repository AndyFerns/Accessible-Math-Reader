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
def latex_to_braille_simple(latex_str):
    """
    Convert LaTeX to a simple char string that braille_converter.py can understand.
    Example: \frac{a}{b} -> (a)/(b)
    Example: a^2 -> a2
    Example: b_i -> bi
    """
    if latex_str.strip().startswith("<math"):
        # This is a simple fallback for MathML. A proper solution
        # would be a full MathML to simple text converter.
        return "MathML(Braille-TBD)"
        
    text = latex_str.strip()
    
    # Simple replacements that map to BRAILLE_MAP
    replacements = [
        # Fractions
        (r'\\frac{(.+?)}{(.+?)}', r'(\1)/(\2)'),
        # Exponents: a^2 -> a2, a^{10} -> a10
        (r'([a-zA-Z0-9]+)\^\{?(.+?)\}?', r'\1\2'),
        # Subscripts: b_i -> bi, b_{10} -> b10
        (r'([a-zA-Z0-9]+)_\{?(.+?)\}?', r'\1\2'),
        # Symbols
        (r'\\pm', '+'), # Simplified from +-
        (r'\\times', '*'),
        (r'\\cdot', '*'),
        (r'\\div', '/'),
        # Remove symbols not in braille map
        (r'[$]', ''), (r'[\\{}]', ''),
        (r'\\sqrt', ''), # No good braille map for 'sqrt'
    ]
    
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    
    # Remove any remaining whitespace
    return text.replace(' ', '')


def parse_math_input(math_str):
    """
    Detect whether input is LaTeX or MathML and return readable text for SPEECH.
    """
    if math_str.strip().startswith("<math"):
        return parse_mathml(math_str)
    else:
        return parse_latex(math_str)