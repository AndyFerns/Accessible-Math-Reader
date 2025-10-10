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


def parse_math_input(math_str):
    """
    Detect whether input is LaTeX or MathML and return readable text.
    """
    if math_str.strip().startswith("<math"):
        return parse_mathml(math_str)
    else:
        return parse_latex(math_str)
