"""!
@file __init__.py
@brief Accessible Math Reader - Screen-reader-first math accessibility toolkit.

@details
This package provides tools for converting mathematical notation (LaTeX, MathML)
into accessible formats including speech output and Braille notation.

@section usage Public API Usage

@code{.py}
from accessible_math_reader import MathReader, VerbosityLevel

# Create a reader instance
reader = MathReader()

# Convert LaTeX to speech text
speech = reader.to_speech(r"\\frac{a}{b}")
# Output: "a divided by b"

# Convert to Nemeth Braille
braille = reader.to_braille(r"\\frac{a}{b}", notation="nemeth")
# Output: "⠹⠁⠌⠃⠼"

# Generate audio file
reader.to_audio(r"\\frac{a}{b}", output_path="output.mp3")
@endcode

@author Accessible Math Reader Contributors
@version 0.1.0
@date 2025
@copyright MIT License
"""

from accessible_math_reader.core.parser import MathParser
from accessible_math_reader.core.semantic import SemanticNode, NodeType
from accessible_math_reader.core.renderer import MathRenderer
from accessible_math_reader.speech.engine import SpeechEngine
from accessible_math_reader.speech.rules import SpeechRuleSet, VerbosityLevel
from accessible_math_reader.braille.nemeth import NemethConverter
from accessible_math_reader.braille.ueb import UEBConverter
from accessible_math_reader.config import Config
from accessible_math_reader.reader import MathReader

__version__ = "0.1.0"
__all__ = [
    # Main interface
    "MathReader",
    # Core components  
    "MathParser",
    "SemanticNode",
    "NodeType",
    "MathRenderer",
    # Speech
    "SpeechEngine",
    "SpeechRuleSet",
    "VerbosityLevel",
    # Braille
    "NemethConverter",
    "UEBConverter",
    # Configuration
    "Config",
]
