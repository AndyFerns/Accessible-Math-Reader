# Accessible Math Reader

> **Screen-reader-first mathematical accessibility toolkit** — convert LaTeX, MathML, and plaintext/Unicode math to speech, Braille, and accessible ARIA HTML.

---

## What is AMR?

Accessible Math Reader (AMR) is a Python toolkit that bridges the gap between mathematical notation and assistive technology. It parses LaTeX, MathML, and everyday plaintext/Unicode math inputs and produces:

| Output | Description |
|---|---|
| **Speech text** | Natural language descriptions at three verbosity levels |
| **Braille** | Nemeth Braille Code (US) and Unified English Braille (international) |
| **Audio files** | MP3 via Google Text-to-Speech |
| **ARIA HTML** | Keyboard-navigable, screen-reader-optimized HTML |

## Three Ways to Use AMR

=== "Python API"

    ```python
    from accessible_math_reader import MathReader

    reader = MathReader()
    print(reader.to_speech(r"\frac{a}{b}"))
    # → "start fraction a over b end fraction"
    ```

=== "CLI"

    ```bash
    amr "\frac{a}{b}" --speech
    amr "\frac{a}{b}" --braille
    amr --interactive
    ```

=== "Web UI"

    ```bash
    pip install -e ".[web]"

    # Development mode (with auto-reload)
    python app.py
    # Open http://localhost:5000

    # Production mode
    python -m accessible_math_reader.server
    # Open http://localhost:5000
    ```

## Quick Links

| | |
|---|---|
| [**Installation**](getting-started/installation.md) | Set up AMR on your machine |
| [**Quick Start**](getting-started/quickstart.md) | Your first conversion in 2 minutes |
| [**API Reference**](api.md) | Full Python API documentation |
| [**Input Formats**](input-formats.md) | Supported LaTeX & MathML syntax |
| [**Configuration**](configuration.md) | Customize speech, Braille, and accessibility settings |
| [**Examples**](examples.md) | Common use cases and code samples |
| [**Architecture**](architecture.md) | System design and module overview |
