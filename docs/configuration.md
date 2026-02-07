# Configuration Guide

> Configure speech, Braille, and accessibility settings for Accessible Math Reader.

---

## Overview

Configuration can be set via:
1. Python API (`Config` class)
2. JSON configuration file
3. Environment variables

Priority: Environment > File > API defaults

---

## Python Configuration

### Basic Setup

```python
from accessible_math_reader import MathReader, Config
from accessible_math_reader.config import (
    SpeechConfig,
    BrailleConfig,
    AccessibilityConfig,
    SpeechStyle,
    BrailleNotation
)

config = Config(
    speech=SpeechConfig(
        style=SpeechStyle.VERBOSE,
        language="en",
        rate=1.0,
        pitch="medium"
    ),
    braille=BrailleConfig(
        notation=BrailleNotation.NEMETH,
        include_indicators=True
    ),
    accessibility=AccessibilityConfig(
        step_by_step=True,
        announce_errors=True,
        default_nav_mode="explore"
    )
)

reader = MathReader(config)
```

### Runtime Updates

```python
# Change verbosity
reader.set_verbosity(SpeechStyle.CONCISE)

# Update full config
reader.config.speech.rate = 0.8
```

---

## Configuration File

### Location

Default paths (checked in order):
1. `./amr-config.json`
2. `~/.config/accessible-math-reader/config.json`
3. `~/.amr-config.json`

### Format

```json
{
  "speech": {
    "style": "verbose",
    "language": "en",
    "rate": 1.0,
    "pitch": "medium",
    "backend": "gtts"
  },
  "braille": {
    "notation": "nemeth",
    "include_indicators": true,
    "line_length": 40
  },
  "accessibility": {
    "step_by_step": true,
    "announce_errors": true,
    "default_nav_mode": "explore",
    "high_contrast": false
  },
  "tts": {
    "backend": "gtts",
    "cache_audio": true,
    "cache_dir": "~/.cache/amr"
  }
}
```

### Loading

```python
config = Config.from_file("my-config.json")
reader = MathReader(config)

# Or use default locations
config = Config.load()
```

---

## Environment Variables

| Variable | Values | Default |
|----------|--------|---------|
| `AMR_SPEECH_STYLE` | verbose, concise, superbrief | verbose |
| `AMR_SPEECH_LANGUAGE` | Language code (en, es, fr) | en |
| `AMR_SPEECH_RATE` | 0.5 - 2.0 | 1.0 |
| `AMR_BRAILLE_NOTATION` | nemeth, ueb | nemeth |
| `AMR_NAV_MODE` | browse, explore, verbose | explore |
| `AMR_HIGH_CONTRAST` | true, false | false |
| `AMR_CONFIG_FILE` | Path to config file | (auto) |

### Example

```bash
# Linux/macOS
export AMR_SPEECH_STYLE=concise
export AMR_BRAILLE_NOTATION=ueb

# Windows PowerShell
$env:AMR_SPEECH_STYLE = "concise"
$env:AMR_BRAILLE_NOTATION = "ueb"
```

### Loading from Environment

```python
config = Config.from_env()
reader = MathReader(config)
```

---

## Settings Reference

### Speech Settings

| Setting | Type | Options | Description |
|---------|------|---------|-------------|
| `style` | enum | verbose, concise, superbrief | Verbosity level |
| `language` | string | Language codes | TTS language |
| `rate` | float | 0.5 - 2.0 | Speech rate |
| `pitch` | string | low, medium, high | Voice pitch |
| `backend` | string | gtts, system | TTS engine |

### Braille Settings

| Setting | Type | Options | Description |
|---------|------|---------|-------------|
| `notation` | enum | nemeth, ueb | Braille standard |
| `include_indicators` | bool | true/false | Include mode indicators |
| `line_length` | int | 20-80 | Max line length |

### Accessibility Settings

| Setting | Type | Options | Description |
|---------|------|---------|-------------|
| `step_by_step` | bool | true/false | Enable stepwise navigation |
| `announce_errors` | bool | true/false | Speak error messages |
| `default_nav_mode` | string | browse, explore, verbose | Initial nav mode |
| `high_contrast` | bool | true/false | High contrast UI |

---

## Web Interface Settings

### Local Storage Keys

| Key | Description |
|-----|-------------|
| `amr-theme` | dark or light |
| `amr-sidebar-collapsed` | Sidebar state |
| `amr-braille-notation` | Selected notation |
| `amr-speech-style` | Verbosity level |
| `amr-nav-mode` | Navigation mode |
| `amr-zoom` | Zoom percentage |
| `amr-history` | Expression history |

### Persistence

Settings are saved in browser localStorage and persist across sessions.

---

## CLI Configuration

### Config Flag

```bash
amr --config my-config.json "\frac{a}{b}"
```

### Inline Options

```bash
amr --speech-style concise "\frac{a}{b}"
amr --braille ueb "\sqrt{x}"
```

### Show Current Config

```bash
amr --show-config
```

---

## Saving Configuration

### Python API

```python
config.save("my-config.json")
```

### CLI

```bash
amr --save-config my-config.json
```
