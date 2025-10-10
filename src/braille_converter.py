BRAILLE_MAP = {
    # Letters
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
    
    # Digits
    '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲',
    '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦', '9': '⠔',
    
    # Basic math symbols
    '+': '⠬', '-': '⠤', '=': '⠿', '*': '⠡', '/': '⠌',
    '(': '⠣', ')': '⠜', '<': '⠪', '>': '⠻', ' ': ' '
}

def math_to_braille(text: str) -> str:
    """Convert basic math text to Braille symbols."""
    result = ""
    for char in text.lower():
        result += BRAILLE_MAP.get(char, char)
    return result
