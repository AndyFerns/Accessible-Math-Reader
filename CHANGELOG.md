# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.1] — 2026-04-08

### ⚠ BREAKING CHANGES

- **Removed `src/` directory entirely.** The legacy modules `src/latex_parser.py`, `src/braille_converter.py`, and `src/speech_converter.py` have been deleted. All math conversion logic is now handled exclusively by the `accessible_math_reader` package via `MathReader`.
- **`app.py` no longer imports from `src/`.** If you have any scripts or tooling that imports from `src.*`, they must be updated to use the `accessible_math_reader` package API instead.
- **`accessible_math_reader/server.py` no longer imports from `src/`.** The WSGI entry point now uses `accessible_math_reader.reader.MathReader` directly and no longer manipulates `sys.path`.

### Changed

- **`app.py`**: Completely rewritten as a thin Flask controller.
  - Imports `MathReader` from `accessible_math_reader.reader` instead of three separate `src/` modules.
  - Uses `reader.to_speech()`, `reader.to_braille()`, and `reader.to_audio()` for the full conversion pipeline.
  - Audio files are now generated with UUID-based filenames (e.g. `a1b2c3d4.mp3`) to prevent overwrite collisions when multiple users submit conversions concurrently.
  - Added `try/except` error handling around the conversion route — invalid expressions now show a friendly error message instead of crashing with a 500 response.
  - Added comprehensive docstrings and inline comments.

- **`accessible_math_reader/server.py`**: Migrated from `src/` imports to `MathReader`.
  - Removed the `sys.path.insert(0, project_root)` hack that was needed to resolve `src/` modules.
  - Uses UUID-based audio filenames and error handling, matching the updated `app.py` pattern.
  - Version bumped from `0.2.0` to `0.5.1` in the file docstring.

- **Version bumped to `0.5.1`** across:
  - `pyproject.toml`
  - `accessible_math_reader/__init__.py`
  - `templates/index.html` (About dialog)

- **`README.md`**: Updated to reflect the new architecture.
  - Removed all references to `src/` from the project structure tree.
  - Updated "Web Interface" section with both `python app.py` (development) and `python -m accessible_math_reader.server` (production) instructions.
  - Updated "Running the Web Server" developer section.
  - Updated version references in the "Releasing as a Package" section.

- **`docs/architecture.md`**: Removed the legacy `src/` modules from the Web Application table and updated Design Decision #4 to reflect the unified architecture.

- **`docs/index.md`**, **`docs/getting-started/quickstart.md`**, **`docs/deployment.md`**: Updated web UI launch instructions to show both development and production commands.

- **`Dockerfile`**: Removed the `COPY src/ src/` line since `src/` no longer exists.

- **`.gitignore`**: Added rules to ignore:
  - `output/` directory contents (generated `.brf` files and other output formats)
  - `*.brf` files globally
  - `*.mp3` and `*.ssml` files in audio directories

### Removed

- **`src/` directory** — The following files were permanently deleted:
  - `src/__init__.py`
  - `src/latex_parser.py` (regex-based LaTeX parser → replaced by `accessible_math_reader.core.parser.MathParser`)
  - `src/braille_converter.py` (character-level Braille map → replaced by `accessible_math_reader.braille.nemeth.NemethConverter`)
  - `src/speech_converter.py` (gTTS wrapper → replaced by `accessible_math_reader.speech.engine.SpeechEngine`)

### Migration Guide

If you were importing from `src/` in any custom scripts:

```python
# ❌ OLD (removed)
from src.latex_parser import parse_math_input
from src.speech_converter import text_to_speech
from src.braille_converter import math_to_braille

# ✅ NEW (v0.5.1+)
from accessible_math_reader import MathReader

reader = MathReader()
speech_text = reader.to_speech(r"\frac{a}{b}")
braille_text = reader.to_braille(r"\frac{a}{b}", notation="nemeth")
audio_path = reader.to_audio(r"\frac{a}{b}", "output.mp3")
```

---

## [0.4.1] — 2026-03-16

### Changed
- UI improvements: minimalistic dark mode, improved spacing and typography.
- Added multi-format clipboard support (copy as LaTeX, accessible text, or Braille).

---

## [0.3.0] — 2026-03-03

### Added
- REST API (`/api/v1/*`) with Flask Blueprint.
- gRPC service interface.
- Docker and Kubernetes deployment support.
- Observability: Prometheus metrics, structured logging.
- Offline TTS backends (pyttsx3, espeak, Coqui).
- Accessibility validation tooling.
- Optional API key authentication and rate limiting.
- Jupyter notebook integration.

---

## [0.2.0] — 2026-02-26

### Added
- `accessible_math_reader` installable Python package with `MathReader` API.
- CLI tool (`amr` command).
- Nemeth and UEB Braille converters.
- Speech verbosity levels (verbose, concise, superbrief).
- ARIA-enhanced keyboard navigation (Browse / Explore / Verbose Learning modes).
- Plugin system for extensibility.
- Configuration via environment variables, JSON files, and Python API.
- MkDocs documentation.

---

## [0.1.0] — 2025-12

### Added
- Initial Flask web application (`app.py`).
- `src/latex_parser.py` — regex-based LaTeX and MathML parser.
- `src/braille_converter.py` — character-level Braille mapper.
- `src/speech_converter.py` — gTTS wrapper.
- `templates/index.html` — accessible dark/light web UI.
- Plaintext and Unicode math input support.
