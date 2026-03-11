"""!
@file speech/pyttsx3_backend.py
@brief Offline TTS backend using pyttsx3.

@details
pyttsx3 uses the operating system's native TTS engine:
  - Windows: SAPI5
  - macOS: NSSpeechSynthesizer
  - Linux: espeak (via C library)

It runs entirely offline with no internet requirement.

Install: ``pip install pyttsx3``  (or ``pip install accessible-math-reader[offline-tts]``)

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import logging
from pathlib import Path

from accessible_math_reader.speech.engine import TTSBackend

logger = logging.getLogger(__name__)


class Pyttsx3Backend(TTSBackend):
    """!
    @brief TTS backend using the pyttsx3 library (native OS voices).

    @details
    Leverages SAPI5 (Windows), NSSpeechSynthesizer (macOS), or
    espeak (Linux) through the pyttsx3 Python package.
    Produces WAV or MP3 output depending on the OS engine.
    """

    def __init__(
        self,
        rate: int = 150,
        volume: float = 1.0,
        voice_id: str | None = None,
    ) -> None:
        """!
        @brief Initialise the pyttsx3 backend.

        @param rate      Speech rate in words per minute (default 150)
        @param volume    Volume 0.0 - 1.0 (default 1.0)
        @param voice_id  Specific voice ID, or None for system default
        """
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id

    # ── TTSBackend interface ──────────────────────────────────────

    def synthesize(self, text: str, output_path: Path) -> Path:
        """!
        @brief Synthesise text to an audio file using pyttsx3.

        @param text         Text to synthesize
        @param output_path  Path for the output audio file
        @return Path to the generated audio file
        @throws ImportError If pyttsx3 is not installed
        """
        try:
            import pyttsx3  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "pyttsx3 is required for this backend. "
                "Install with: pip install pyttsx3"
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        engine = pyttsx3.init()
        engine.setProperty("rate", self.rate)
        engine.setProperty("volume", self.volume)

        if self.voice_id:
            engine.setProperty("voice", self.voice_id)

        engine.save_to_file(text, str(output_path))
        engine.runAndWait()

        logger.info("pyttsx3 wrote audio to %s", output_path)
        return output_path

    @property
    def supports_ssml(self) -> bool:
        """pyttsx3 does not support SSML."""
        return False

    @classmethod
    def is_available(cls) -> bool:
        """!
        @brief Check if pyttsx3 is installed.

        @return True if the package can be imported
        """
        try:
            import pyttsx3  # type: ignore[import-untyped]  # noqa: F401
            return True
        except ImportError:
            return False
