"""!
@file reader.py
@brief Main high-level interface for Accessible Math Reader.

@details
Provides the primary user-facing API that combines parsing, speech
generation, and Braille conversion into a simple, unified interface.

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from accessible_math_reader.config import Config
from accessible_math_reader.core.parser import MathParser
from accessible_math_reader.core.semantic import SemanticNode, MathNavigator
from accessible_math_reader.core.renderer import MathRenderer
from accessible_math_reader.speech.engine import SpeechEngine
from accessible_math_reader.speech.rules import VerbosityLevel


class MathReader:
    """!
    @brief Main interface for the Accessible Math Reader.
    
    @details
    This is the primary class users should interact with. It provides
    a simple API for converting mathematical notation to accessible formats.
    
    @section reader_example Basic Usage
    @code{.py}
    from accessible_math_reader import MathReader
    
    # Create reader with default settings
    reader = MathReader()
    
    # Convert LaTeX to speech
    speech = reader.to_speech(r"\\frac{a}{b}")
    print(speech)  # "start fraction a over b end fraction"
    
    # Convert to Braille
    braille = reader.to_braille(r"\\frac{a}{b}")
    print(braille)  # Nemeth Braille output
    
    # Generate audio file
    audio_path = reader.to_audio(r"\\frac{a}{b}", "output.mp3")
    @endcode
    
    @section reader_config Custom Configuration
    @code{.py}
    from accessible_math_reader import MathReader, Config
    from accessible_math_reader.config import SpeechConfig, SpeechStyle
    
    config = Config(
        speech=SpeechConfig(style=SpeechStyle.CONCISE)
    )
    reader = MathReader(config)
    
    # Concise output
    speech = reader.to_speech(r"\\frac{a}{b}")
    print(speech)  # "a over b"
    @endcode
    """
    
    def __init__(self, config: Optional[Config] = None) -> None:
        """!
        @brief Initialize the MathReader.
        
        @param config Configuration object (uses defaults if None)
        """
        self.config = config or Config()
        self._parser = MathParser()
        self._renderer = MathRenderer(self.config)
        self._speech_engine = SpeechEngine(self.config)
    
    def parse(self, math_input: str) -> SemanticNode:
        """!
        @brief Parse mathematical input to semantic tree.
        
        @details
        Accepts LaTeX or MathML input and returns a semantic
        representation suitable for further processing.
        
        @param math_input LaTeX or MathML string
        @return Root SemanticNode of the parsed expression
        @throws ParseError If parsing fails
        """
        return self._parser.parse(math_input)
    
    def to_speech(self, math_input: str) -> str:
        """!
        @brief Convert mathematical input to speech text.
        
        @details
        Parses the input and generates a natural language
        description suitable for text-to-speech or screen readers.
        
        @param math_input LaTeX or MathML string
        @return Spoken text representation
        """
        tree = self.parse(math_input)
        return self._renderer.to_speech(tree)
    
    def to_braille(
        self, 
        math_input: str, 
        notation: str = "nemeth"
    ) -> str:
        """!
        @brief Convert mathematical input to Braille.
        
        @param math_input LaTeX or MathML string
        @param notation Braille notation: "nemeth" or "ueb"
        @return Braille string
        """
        tree = self.parse(math_input)
        return self._renderer.to_braille(tree, notation=notation)
    
    def to_audio(
        self, 
        math_input: str,
        output_path: str = "output.mp3"
    ) -> Path:
        """!
        @brief Convert mathematical input to audio file.
        
        @param math_input LaTeX or MathML string
        @param output_path Path for output audio file
        @return Path to generated audio file
        """
        speech_text = self.to_speech(math_input)
        return self._speech_engine.synthesize(speech_text, output_path)
    
    def to_ssml(self, math_input: str) -> str:
        """!
        @brief Convert mathematical input to SSML.
        
        @details
        Generates SSML markup with math-appropriate prosody
        for use with SSML-capable TTS engines.
        
        @param math_input LaTeX or MathML string
        @return SSML string
        """
        speech_text = self.to_speech(math_input)
        return self._speech_engine.to_math_ssml(speech_text)
    
    def get_navigator(self, math_input: str) -> MathNavigator:
        """!
        @brief Get a navigator for step-by-step exploration.
        
        @details
        Creates a navigator that allows keyboard-based traversal
        of the mathematical expression.
        
        @param math_input LaTeX or MathML string
        @return MathNavigator instance
        """
        tree = self.parse(math_input)
        return MathNavigator(tree)
    
    def get_structure(self, math_input: str) -> dict:
        """!
        @brief Get the structural representation of an expression.
        
        @details
        Returns a dictionary representation of the semantic tree,
        useful for debugging or building custom renderers.
        
        @param math_input LaTeX or MathML string
        @return Dictionary representation of the expression
        """
        tree = self.parse(math_input)
        return tree.to_dict()
    
    def set_verbosity(self, level: str | VerbosityLevel) -> None:
        """!
        @brief Change the speech verbosity level.
        
        @param level Verbosity: "verbose", "concise", or "superbrief"
        """
        if isinstance(level, str):
            level = VerbosityLevel(level)
        
        from accessible_math_reader.config import SpeechStyle
        self.config.speech.style = SpeechStyle(level.value)
        
        # Recreate renderer with new config
        self._renderer = MathRenderer(self.config)
