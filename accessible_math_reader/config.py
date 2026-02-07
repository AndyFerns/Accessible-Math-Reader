"""!
@file config.py
@brief Configuration management for Accessible Math Reader.

@details
Provides a centralized configuration system with sensible defaults
and support for environment variables, config files, and runtime overrides.

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class BrailleNotation(Enum):
    """!
    @brief Supported Braille notation systems.
    
    @details
    - NEMETH: Nemeth Braille Code for mathematics, widely used in US
    - UEB: Unified English Braille, international standard
    """
    NEMETH = "nemeth"
    UEB = "ueb"


class NavigationMode(Enum):
    """!
    @brief Navigation modes for math exploration.
    
    @details
    Different modes provide different levels of detail and interaction:
    - BROWSE: High-level overview, jump between major terms
    - EXPLORE: Detailed tree navigation, interactive drilling down
    - VERBOSE_LEARNING: Extended descriptions with pedagogical hints
    """
    BROWSE = "browse"                   # High-level navigation
    EXPLORE = "explore"                 # Interactive exploration
    VERBOSE_LEARNING = "verbose"        # Learning mode with hints


class SpeechStyle(Enum):
    """!
    @brief Speech output style preferences.
    
    @details
    - VERBOSE: Full descriptions (e.g., "the fraction a over b end fraction")
    - CONCISE: Shorter form (e.g., "a over b")
    - SUPERBRIEF: Minimal (e.g., "a b fraction")
    """
    VERBOSE = "verbose"
    CONCISE = "concise"
    SUPERBRIEF = "superbrief"


@dataclass
class SpeechConfig:
    """!
    @brief Configuration for speech output.
    
    @param style Speech verbosity style
    @param language Language code for TTS (e.g., "en", "en-US")
    @param rate Speech rate multiplier (1.0 = normal)
    @param announce_structure Whether to announce structure (start/end of fractions, etc.)
    """
    style: SpeechStyle = SpeechStyle.VERBOSE
    language: str = "en"
    rate: float = 1.0
    announce_structure: bool = True


@dataclass
class BrailleConfig:
    """!
    @brief Configuration for Braille output.
    
    @param notation Braille notation system to use
    @param include_indicators Whether to include numeric/letter indicators
    @param output_format Output format: "unicode", "brf" (Braille Ready Format), "ascii"
    @param line_width Maximum line width for BRF output (default: 40 chars)
    @param prefer_spoken_over_braille User preference for primary output type
    @param cache_braille Enable caching of Braille generation for performance
    @param unsupported_fallback How to handle unsupported constructs: "describe", "warn", "error"
    """
    notation: BrailleNotation = BrailleNotation.NEMETH
    include_indicators: bool = True
    
    # === PHASE 3 ENHANCEMENTS ===
    # Output format control for different use cases
    output_format: str = "unicode"          # "unicode" | "brf" | "ascii"
    line_width: int = 40                    # For BRF embosser output
    
    # User preferences
    prefer_spoken_over_braille: bool = False  # Primary modality preference
    
    # Performance and error handling
    cache_braille: bool = True                # Enable Braille caching
    unsupported_fallback: str = "describe"    # "describe" | "warn" | "error"


@dataclass
class AccessibilityConfig:
    """!
    @brief Accessibility-specific configuration.
    
    @param announce_errors Whether to provide accessible error messages
    @param step_by_step Enable step-by-step navigation mode
    @param highlight_current Highlight currently focused sub-expression
    @param navigation_mode Current navigation mode (BROWSE/EXPLORE/VERBOSE_LEARNING)
    @param aria_live_politeness Politeness level for ARIA live regions
    @param focus_indicator_style CSS class for focus indicator styling
    @param enable_progressive_disclosure Collapse complex expressions by default
    @param enable_context_help Enable "Where am I?" feature
    @param reduced_motion Respect prefers-reduced-motion user setting
    @param high_contrast Support high contrast mode
    """
    # Original settings
    announce_errors: bool = True
    step_by_step: bool = True
    highlight_current: bool = True
    
    # === PHASE 2: ARIA NAVIGATION ENHANCEMENTS ===
    # Navigation mode controls level of detail and interaction
    navigation_mode: NavigationMode = NavigationMode.EXPLORE
    
    # ARIA live region configuration for announcements
    aria_live_politeness: str = "polite"    # "off" | "polite" | "assertive"
    
    # Focus visualization
    focus_indicator_style: str = "default"  # CSS class name for custom styling
    
    # === PHASE 5: PROGRESSIVE FEATURES ===
    # Progressive disclosure for complex expressions
    enable_progressive_disclosure: bool = True
    
    # Context help and "Where am I?" feature
    enable_context_help: bool = True
    
    # === PHASE 4: FRONTEND ACCESSIBILITY ===
    # Respect user motion and contrast preferences
    reduced_motion: bool = False            # Will be auto-detected from prefers-reduced-motion
    high_contrast: bool = False             # Will be auto-detected from prefers-contrast


@dataclass 
class Config:
    """!
    @brief Main configuration container for Accessible Math Reader.
    
    @details
    Aggregates all configuration options and provides methods for
    loading from files and environment variables.
    
    @section config_example Example Usage
    @code{.py}
    from accessible_math_reader import Config
    from accessible_math_reader.config import SpeechStyle, BrailleNotation
    
    # Use defaults
    config = Config()
    
    # Customize
    config = Config(
        speech=SpeechConfig(style=SpeechStyle.CONCISE),
        braille=BrailleConfig(notation=BrailleNotation.UEB)
    )
    
    # Load from file
    config = Config.from_file("config.json")
    @endcode
    """
    speech: SpeechConfig = field(default_factory=SpeechConfig)
    braille: BrailleConfig = field(default_factory=BrailleConfig)
    accessibility: AccessibilityConfig = field(default_factory=AccessibilityConfig)
    
    # Plugin configuration
    plugin_dirs: list[str] = field(default_factory=list)
    enabled_plugins: list[str] = field(default_factory=list)
    
    @classmethod
    def from_file(cls, path: str | Path) -> Config:
        """!
        @brief Load configuration from a JSON file.
        
        @param path Path to the configuration file
        @return Config instance with loaded settings
        @throws FileNotFoundError If config file doesn't exist
        @throws json.JSONDecodeError If config file is invalid JSON
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls._from_dict(data)
    
    @classmethod
    def from_env(cls) -> Config:
        """!
        @brief Load configuration from environment variables.
        
        @details
        Supported environment variables:
        - AMR_SPEECH_STYLE: verbose, concise, or superbrief
        - AMR_SPEECH_LANGUAGE: Language code (e.g., en, en-US)
        - AMR_BRAILLE_NOTATION: nemeth or ueb
        - AMR_PLUGIN_DIRS: Colon-separated list of plugin directories
        
        @return Config instance with settings from environment
        """
        config = cls()
        
        if style := os.environ.get("AMR_SPEECH_STYLE"):
            config.speech.style = SpeechStyle(style.lower())
        
        if lang := os.environ.get("AMR_SPEECH_LANGUAGE"):
            config.speech.language = lang
            
        if notation := os.environ.get("AMR_BRAILLE_NOTATION"):
            config.braille.notation = BrailleNotation(notation.lower())
            
        if plugin_dirs := os.environ.get("AMR_PLUGIN_DIRS"):
            config.plugin_dirs = plugin_dirs.split(os.pathsep)
            
        return config
    
    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Config:
        """!
        @brief Create Config from a dictionary.
        
        @param data Dictionary with configuration values
        @return Config instance
        """
        speech_data = data.get("speech", {})
        braille_data = data.get("braille", {})
        a11y_data = data.get("accessibility", {})
        
        speech = SpeechConfig(
            style=SpeechStyle(speech_data.get("style", "verbose")),
            language=speech_data.get("language", "en"),
            rate=speech_data.get("rate", 1.0),
            announce_structure=speech_data.get("announce_structure", True),
        )
        
        braille = BrailleConfig(
            notation=BrailleNotation(braille_data.get("notation", "nemeth")),
            include_indicators=braille_data.get("include_indicators", True),
        )
        
        accessibility = AccessibilityConfig(
            announce_errors=a11y_data.get("announce_errors", True),
            step_by_step=a11y_data.get("step_by_step", True),
            highlight_current=a11y_data.get("highlight_current", True),
        )
        
        return cls(
            speech=speech,
            braille=braille,
            accessibility=accessibility,
            plugin_dirs=data.get("plugin_dirs", []),
            enabled_plugins=data.get("enabled_plugins", []),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """!
        @brief Convert configuration to a dictionary.
        
        @return Dictionary representation of configuration
        """
        return {
            "speech": {
                "style": self.speech.style.value,
                "language": self.speech.language,
                "rate": self.speech.rate,
                "announce_structure": self.speech.announce_structure,
            },
            "braille": {
                "notation": self.braille.notation.value,
                "include_indicators": self.braille.include_indicators,
            },
            "accessibility": {
                "announce_errors": self.accessibility.announce_errors,
                "step_by_step": self.accessibility.step_by_step,
                "highlight_current": self.accessibility.highlight_current,
            },
            "plugin_dirs": self.plugin_dirs,
            "enabled_plugins": self.enabled_plugins,
        }
    
    def save(self, path: str | Path) -> None:
        """!
        @brief Save configuration to a JSON file.
        
        @param path Path to save the configuration file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
