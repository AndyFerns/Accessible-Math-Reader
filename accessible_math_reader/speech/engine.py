"""!
@file speech/engine.py
@brief Text-to-speech engine abstraction.

@details
Provides a unified interface for TTS engines, with gTTS as the default
backend and support for SSML generation.

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from accessible_math_reader.config import Config


class TTSBackend(ABC):
    """!
    @brief Abstract base class for TTS backends.
    
    @details
    Defines the interface that TTS implementations must provide.
    Enables swapping between gTTS, pyttsx3, cloud services, etc.
    """
    
    @abstractmethod
    def synthesize(self, text: str, output_path: Path) -> Path:
        """!
        @brief Convert text to audio file.
        
        @param text Text to synthesize
        @param output_path Path for output audio file
        @return Path to the generated audio file
        """
        pass
    
    @property
    @abstractmethod
    def supports_ssml(self) -> bool:
        """!
        @brief Check if backend supports SSML.
        
        @return True if SSML is supported
        """
        pass


class GTTSBackend(TTSBackend):
    """!
    @brief Google Text-to-Speech (gTTS) backend.
    
    @details
    Uses the gTTS library for speech synthesis. Free but requires
    internet connection. Does not support SSML.
    """
    
    def __init__(self, language: str = "en") -> None:
        """!
        @brief Initialize gTTS backend.
        
        @param language Language code (e.g., "en", "en-US")
        """
        self.language = language
    
    def synthesize(self, text: str, output_path: Path) -> Path:
        """!
        @brief Synthesize speech using gTTS.
        
        @param text Text to synthesize
        @param output_path Output file path
        @return Path to generated audio
        @throws ImportError If gTTS is not installed
        """
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError("gTTS is required. Install with: pip install gtts")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        tts = gTTS(text=text, lang=self.language)
        tts.save(str(output_path))
        
        return output_path
    
    @property
    def supports_ssml(self) -> bool:
        """gTTS does not support SSML."""
        return False


class SpeechEngine:
    """!
    @brief High-level speech synthesis engine.
    
    @details
    Coordinates between speech text generation and TTS synthesis,
    with support for SSML and multiple backends.
    
    @section engine_example Example Usage
    @code{.py}
    from accessible_math_reader.speech.engine import SpeechEngine
    
    engine = SpeechEngine()
    
    # Synthesize to file
    path = engine.synthesize("a divided by b", "output.mp3")
    
    # Generate SSML (for compatible engines)
    ssml = engine.to_ssml("a divided by b")
    @endcode
    """
    
    def __init__(self, config: Config | None = None) -> None:
        """!
        @brief Initialize speech engine.
        
        @param config Configuration object
        """
        if config is None:
            from accessible_math_reader.config import Config
            config = Config()
        self.config = config
        
        # Default to gTTS backend
        self._backend: TTSBackend = GTTSBackend(
            language=config.speech.language
        )
    
    def set_backend(self, backend: TTSBackend) -> None:
        """!
        @brief Set a custom TTS backend.
        
        @param backend TTS backend implementation
        """
        self._backend = backend
    
    def synthesize(
        self, 
        text: str, 
        output_path: str | Path = "output.mp3"
    ) -> Path:
        """!
        @brief Synthesize text to audio file.
        
        @param text Text to synthesize
        @param output_path Output file path
        @return Path to generated audio
        """
        output_path = Path(output_path)
        return self._backend.synthesize(text, output_path)
    
    def to_ssml(
        self, 
        text: str,
        rate: Optional[float] = None,
        pitch: Optional[str] = None
    ) -> str:
        """!
        @brief Generate SSML markup for text.
        
        @details
        Creates SSML that can be used with compatible TTS engines
        for enhanced prosody control.
        
        @param text Plain text to wrap in SSML
        @param rate Speech rate (0.5 = half speed, 2.0 = double speed)
        @param pitch Pitch adjustment ("low", "medium", "high")
        @return SSML string
        """
        rate = rate or self.config.speech.rate
        pitch = pitch or "medium"
        
        # Convert rate to percentage
        rate_percent = f"{int(rate * 100)}%"
        
        ssml = f'''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis">
    <prosody rate="{rate_percent}" pitch="{pitch}">
        {self._escape_ssml(text)}
    </prosody>
</speak>'''
        return ssml.strip()
    
    def to_math_ssml(self, text: str) -> str:
        """!
        @brief Generate math-optimized SSML.
        
        @details
        Adds pauses and emphasis appropriate for mathematical content.
        
        @param text Math speech text
        @return SSML with math-appropriate prosody
        """
        # Add pauses around structural words
        text = text.replace(" over ", ' <break time="200ms"/> over <break time="200ms"/> ')
        text = text.replace("start fraction", '<break time="100ms"/> start fraction')
        text = text.replace("end fraction", 'end fraction <break time="100ms"/>')
        text = text.replace("to the power of", '<break time="100ms"/> to the power of')
        
        return self.to_ssml(text)
    
    def _escape_ssml(self, text: str) -> str:
        """Escape special XML characters in SSML."""
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))
