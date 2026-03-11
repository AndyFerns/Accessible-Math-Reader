"""!
@file speech/espeak_backend.py
@brief Offline TTS backend using eSpeak-NG.

@details
eSpeak-NG is a free, open-source speech synthesizer available on
Linux (``apt install espeak-ng``), macOS (``brew install espeak``),
and Windows (installer from GitHub).  It runs entirely offline and
produces intelligible, if somewhat robotic, speech.

This backend calls ``espeak-ng`` via subprocess, producing a WAV
file that is then available at the output path.

@section espeak_usage Usage
@code{.py}
from accessible_math_reader.speech.engine import SpeechEngine
from accessible_math_reader.speech.espeak_backend import ESpeakBackend

engine = SpeechEngine()
engine.set_backend(ESpeakBackend(language="en", speed=150))
engine.synthesize("a plus b", "output.wav")
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from accessible_math_reader.speech.engine import TTSBackend

logger = logging.getLogger(__name__)


class ESpeakBackend(TTSBackend):
    """!
    @brief TTS backend using eSpeak-NG via subprocess.

    @details
    Requires ``espeak-ng`` (or ``espeak``) to be installed and
    available on ``PATH``.  Produces WAV output.
    """

    def __init__(
        self,
        language: str = "en",
        speed: int = 150,
        pitch: int = 50,
    ) -> None:
        """!
        @brief Initialise the eSpeak backend.

        @param language  Voice language (e.g. "en", "en-us")
        @param speed     Words per minute (default 150)
        @param pitch     Pitch 0-99 (default 50)
        """
        self.language = language
        self.speed = speed
        self.pitch = pitch

        # Find the executable
        self._executable = shutil.which("espeak-ng") or shutil.which("espeak")
        if self._executable:
            logger.info("eSpeak found at %s", self._executable)
        else:
            logger.warning(
                "eSpeak not found on PATH — synthesis will fail. "
                "Install with: apt install espeak-ng (Linux) / "
                "brew install espeak (macOS)"
            )

    # ── TTSBackend interface ──────────────────────────────────────

    def synthesize(self, text: str, output_path: Path) -> Path:
        """!
        @brief Synthesise text to a WAV file using eSpeak.

        @param text         Text to synthesize
        @param output_path  Path for the output audio file
        @return Path to the generated WAV file
        @throws RuntimeError If eSpeak is not installed
        @throws subprocess.CalledProcessError If synthesis fails
        """
        if self._executable is None:
            raise RuntimeError(
                "eSpeak is not installed. Install with: "
                "apt install espeak-ng (Linux) / brew install espeak (macOS)"
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            self._executable,
            "-v", self.language,
            "-s", str(self.speed),
            "-p", str(self.pitch),
            "-w", str(output_path),   # write to WAV file
            text,
        ]

        logger.debug("Running: %s", " ".join(cmd))
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    @property
    def supports_ssml(self) -> bool:
        """eSpeak supports a subset of SSML."""
        return True

    @classmethod
    def is_available(cls) -> bool:
        """!
        @brief Check if eSpeak is installed on the system.

        @return True if ``espeak-ng`` or ``espeak`` is on PATH
        """
        return bool(shutil.which("espeak-ng") or shutil.which("espeak"))
