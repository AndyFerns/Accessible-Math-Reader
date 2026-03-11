"""!
@file speech/coqui_backend.py
@brief Offline TTS backend using Coqui TTS.

@details
Coqui TTS provides high-quality neural text-to-speech that runs
entirely offline.  Models are downloaded once and cached locally.

Install: ``pip install TTS`` (Coqui's package name on PyPI)

This backend is significantly heavier than eSpeak or pyttsx3 but
produces much more natural-sounding speech.

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import logging
from pathlib import Path

from accessible_math_reader.speech.engine import TTSBackend

logger = logging.getLogger(__name__)


class CoquiBackend(TTSBackend):
    """!
    @brief TTS backend using the Coqui TTS neural engine.

    @details
    Uses the ``TTS`` library for high-quality offline synthesis.
    The default model (``tts_models/en/ljspeech/tacotron2-DDC``)
    is automatically downloaded on first use (~200 MB).
    """

    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        gpu: bool = False,
    ) -> None:
        """!
        @brief Initialise the Coqui TTS backend.

        @param model_name  Coqui TTS model identifier
        @param gpu         Use GPU if available (default False)
        """
        self.model_name = model_name
        self.gpu = gpu
        self._tts = None  # lazily initialised

    def _get_tts(self):
        """Lazy-load the TTS model."""
        if self._tts is None:
            try:
                from TTS.api import TTS  # type: ignore[import-untyped]
            except ImportError:
                raise ImportError(
                    "Coqui TTS is required. Install with: pip install TTS"
                )
            logger.info(
                "Loading Coqui TTS model: %s (gpu=%s)",
                self.model_name, self.gpu,
            )
            self._tts = TTS(model_name=self.model_name, gpu=self.gpu)
        return self._tts

    # ── TTSBackend interface ──────────────────────────────────────

    def synthesize(self, text: str, output_path: Path) -> Path:
        """!
        @brief Synthesise text using a Coqui neural TTS model.

        @param text         Text to synthesize
        @param output_path  Path for the output audio file (WAV)
        @return Path to the generated audio file
        @throws ImportError If Coqui TTS is not installed
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        tts = self._get_tts()
        tts.tts_to_file(text=text, file_path=str(output_path))

        logger.info("Coqui TTS wrote audio to %s", output_path)
        return output_path

    @property
    def supports_ssml(self) -> bool:
        """Coqui TTS does not support SSML natively."""
        return False

    @classmethod
    def is_available(cls) -> bool:
        """!
        @brief Check if Coqui TTS is installed.

        @return True if the TTS package can be imported
        """
        try:
            from TTS.api import TTS  # type: ignore[import-untyped]  # noqa: F401
            return True
        except ImportError:
            return False
