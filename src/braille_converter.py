BRAILLE_MAP = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙',
    'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓',
    'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇',
    'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏',
    'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
    'y': '⠽', 'z': '⠵', '+': '⠬', '-': '⠤',
    '=': '⠿', '(': '⠣', ')': '⠜'
}

def math_to_braille(text: str) -> str:
    """Convert basic math text to Braille symbols."""
    result = ""
    for char in text.lower():
        result += BRAILLE_MAP.get(char, char)
    return result
