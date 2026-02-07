# Accessible Math Reader

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)

> **Screen-reader-first mathematical accessibility toolkit** for converting LaTeX/MathML to speech, Braille, and accessible formats.

---

## ✨ Features

- **📖 Multi-Format Input**: Parse LaTeX and MathML mathematical expressions
- **🔊 Speech Output**: Natural language descriptions with configurable verbosity
- **⠿ Braille Support**: Nemeth and UEB (Unified English Braille) notation
- **♿ ARIA Navigation**: Keyboard-accessible exploration of math structure
- **📋 Multi-Format Clipboard**: Copy formulas as LaTeX, accessible text, or Braille
- **🎨 Accessible Web UI**: Dark/light themes, high contrast mode

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/accessible-math-reader.git
cd accessible-math-reader

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e ".[dev,web]"
```

### Basic Usage (Python API)

```python
from accessible_math_reader import MathReader

# Create reader instance
reader = MathReader()

# Convert LaTeX to speech
speech = reader.to_speech(r"\frac{a}{b}")
print(speech)  # "start fraction a over b end fraction"

# Convert to Nemeth Braille
braille = reader.to_braille(r"\frac{a}{b}", notation="nemeth")
print(braille)  # "⠹⠁⠌⠃⠼"

# Generate audio file
reader.to_audio(r"\frac{a}{b}", "output.mp3")
```

### Command Line Interface

```bash
# Speech output
amr "\frac{a^2 + b^2}{c}" --speech

# Braille output (Nemeth)
amr "\frac{a}{b}" --braille nemeth

# Interactive mode
amr --interactive
```

### Web Interface

```bash
# Run Flask development server
python app.py

# Open http://localhost:5000
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/api.md) | Full Python API documentation |
| [Input Formats](docs/input-formats.md) | Supported LaTeX and MathML syntax |
| [Accessibility Guide](docs/accessibility.md) | Screen reader, Braille, and ARIA features |
| [Configuration](docs/configuration.md) | Speech, Braille, and navigation settings |
| [Examples](docs/examples.md) | Common use cases and code samples |

---

## 🏗️ Architecture

```
accessible_math_reader/
├── core/                 # Core parsing and rendering
│   ├── parser.py        # LaTeX/MathML parser
│   ├── semantic.py      # Semantic AST representation
│   ├── renderer.py      # Base rendering infrastructure
│   ├── aria_navigator.py # ARIA navigation with modes
│   └── aria_renderer.py # Accessible HTML generation
├── speech/              # Speech output
│   ├── engine.py        # TTS engine abstraction
│   └── rules.py         # Verbosity-based speech rules
├── braille/             # Braille conversion
│   ├── nemeth.py        # Nemeth Braille Code
│   └── ueb.py           # Unified English Braille
├── config.py            # Configuration management
├── reader.py            # High-level API
└── cli.py               # Command-line interface
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AMR_SPEECH_STYLE` | verbose, concise, superbrief | verbose |
| `AMR_BRAILLE_NOTATION` | nemeth, ueb | nemeth |
| `AMR_SPEECH_LANGUAGE` | TTS language code | en |

### Config File

```json
{
  "speech": {
    "style": "verbose",
    "language": "en",
    "rate": 1.0
  },
  "braille": {
    "notation": "nemeth",
    "include_indicators": true
  },
  "accessibility": {
    "step_by_step": true,
    "announce_errors": true
  }
}
```

---

## 🎯 Accessibility Compliance

- **WCAG 2.2 AA**: Full compliance for web interface
- **WAI-ARIA**: Proper roles, labels, and live regions
- **Screen Readers**: Tested with NVDA, JAWS, VoiceOver
- **Braille Displays**: Unicode Braille output compatible with refreshable displays

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter
ruff check accessible_math_reader/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [MathJax](https://www.mathjax.org/) for mathematical rendering
- [gTTS](https://gtts.readthedocs.io/) for text-to-speech
- [WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/) for accessibility guidelines
