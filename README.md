<p align="center">
  <h1 align="center">♿ Accessible Math Reader</h1>
  <p align="center">
    <strong>A screen-reader-first mathematical accessibility toolkit for converting LaTeX, MathML, and plaintext/Unicode math into speech, Braille, and navigable ARIA structures.</strong>
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.9+-green.svg" alt="Python 3.9+"></a>
  <a href="#"><img src="https://img.shields.io/badge/Status-Alpha-orange.svg" alt="Alpha"></a>
  <a href="https://www.w3.org/WAI/standards-guidelines/wcag/"><img src="https://img.shields.io/badge/WCAG-2.2_AA-purple.svg" alt="WCAG 2.2 AA"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="docs/api.md">API Reference</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 📖 Overview

**Accessible Math Reader (AMR)** is a Python package and web application that makes mathematical notation accessible to visually impaired users. It parses LaTeX, MathML, and plaintext/Unicode math expressions and converts them into:

- **Natural language speech** with configurable verbosity (verbose, concise, superbrief)
- **Braille notation** in both Nemeth (US standard) and UEB (international standard)
- **Audio files** via Google Text-to-Speech (gTTS)
- **ARIA-annotated HTML** for keyboard-navigable, screen-reader-friendly exploration

AMR can be used as a **Python library**, a **CLI tool**, or through a **Flask-based web interface**.

> 🎓 Developed at FCRIT Vashi as a project in academic research in accessibility and inclusive technology.

---

## ✨ Features

| Category | Highlights |
|---|---|
| **📖 Multi-Format Input** | Parse LaTeX, MathML, and plaintext/Unicode math expressions with auto-detection |
| **🔊 Speech Output** | Natural language descriptions with 3 verbosity levels and SSML support |
| **⠿ Braille Support** | Full Nemeth Braille Code and Unified English Braille (UEB) converters |
| **♿ ARIA Navigation** | Keyboard-accessible, step-by-step expression exploration with 3 navigation modes |
| **📋 Multi-Format Clipboard** | Copy formulas as LaTeX, accessible text, or Braille from the web UI |
| **🎨 Accessible Web UI** | Dark/light themes, high-contrast mode, zoom controls, screen-reader optimized |
| **🔌 Plugin System** | Extensible architecture for custom speech rules, Braille notations, and input formats |
| **⌨️ CLI Tool** | Full-featured command-line interface with interactive and batch modes |

---

## 🏗️ Architecture

```plaintext
┌─────────────────────────────────────────────────────────────────────┐
│                        Accessible Math Reader                       │
├──────────┬──────────┬───────────────────────────────┬───────────────┤
│  CLI     │  Web UI  │      Python API (MathReader)  │   Plugins     │
│  (amr)   │  (Flask) │                               │  (extensible) │
├──────────┴──────────┴───────────────────────────────┴───────────────┤
│                        Core Pipeline                                │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────────────────┐   │
│  │  Parser  │──▸│ Semantic AST │──▸│        Renderers           │   │
│  │  LaTeX   │   │ (SemanticNode│   │  ┌─────────┬────────────┐  │   │
│  │  MathML  │   │  NodeType)   │   │  │ Speech  │  Braille   │  │   │
│  │ Plaintext│   |              |   |  |         |            |  |   |
│  └──────────┘   └──────┬───────┘   │  │ Engine  │ Nemeth/UEB │  │   │
│                        │           │  └─────────┴────────────┘  │   │
│                        ▼           │  ┌─────────┬────────────┐  │   │
│                  ┌───────────┐     │  │  ARIA   │  Simple    │  │   │
│                  │ Navigator │     │  │Renderer │  Text      │  │   │
│                  │ (keyboard │     │  └─────────┴────────────┘  │   │
│                  │  explore) │     └────────────────────────────┘   │
│                  └───────────┘                                      │
├─────────────────────────────────────────────────────────────────────┤
│                        Configuration                                │
│        Config  ·  SpeechConfig  ·  BrailleConfig  ·  A11yConfig     │
└─────────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
accessible-math-reader/
├── accessible_math_reader/       # 📦 Installable Python package
│   ├── __init__.py               #    Public API exports
│   ├── reader.py                 #    MathReader — high-level unified interface
│   ├── server.py                 #    WSGI entry point for production deployment
│   ├── cli.py                    #    CLI entry point (`amr` command)
│   ├── config.py                 #    Configuration management (env, file, API)
│   ├── core/                     #    Core parsing & rendering engine
│   │   ├── parser.py             #      LaTeX / MathML / Plaintext → Semantic AST
│   │   ├── semantic.py           #      SemanticNode, NodeType, MathNavigator
│   │   ├── renderer.py           #      Base rendering infrastructure
│   │   ├── aria_navigator.py     #      ARIA-enhanced keyboard navigation
│   │   ├── aria_renderer.py      #      Accessible HTML generation
│   │   └── accessibility_contract.py  #  Accessibility validation contracts
│   ├── speech/                   #    Speech output subsystem
│   │   ├── engine.py             #      TTS engine abstraction (gTTS backend)
│   │   └── rules.py              #      Verbosity-based speech rules
│   ├── braille/                  #    Braille conversion subsystem
│   │   ├── nemeth.py             #      Nemeth Braille Code converter
│   │   └── ueb.py                #      Unified English Braille converter
│   └── plugins/                  #    Plugin system
│       └── base.py               #      Abstract plugin base classes
├── app.py                        # 🌐 Flask web application (dev entry point)
├── templates/
│   └── index.html                # 🖥️  Web UI template (dark/light, accessible)
├── static/
│   ├── css/style.css             #    Web UI styles
│   └── js/
│       ├── app.js                #    Frontend logic & keyboard shortcuts
│       └── clipboard.js          #    Multi-format clipboard support
├── docs/                         # 📚 Documentation
│   ├── api.md                    #    Full Python API reference
│   ├── input-formats.md          #    Supported LaTeX & MathML syntax
│   ├── accessibility.md          #    Screen reader, Braille & ARIA guide
│   ├── configuration.md          #    Configuration reference
│   └── examples.md               #    Code samples & use cases
├── CHANGELOG.md                  #    Version history and migration notes
├── pyproject.toml                #    Package metadata & build config
├── requirements.txt              #    Web-app-specific dependencies
└── LICENSE                       #    MIT License
```

---

## 🚀 Installation

### As a Python Package (Recommended)

Install directly from the repository:

```bash
# Clone the repository
git clone https://github.com/AndyFerns/Accessible-Math-Reader.git
cd Accessible-Math-Reader

# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# Install the package in editable mode (with all extras)
pip install -e ".[dev,web]"
```

This installs AMR as a package and registers the `amr` CLI command.

### Minimal Install (Library Only)

If you only need the Python API (no web UI, no dev tools):

```bash
pip install -e .
```

Core dependencies are just `gtts` and `lxml`.

### From PyPI *(coming soon)*

```bash
pip install accessible-math-reader
```

---

## 📋 Usage

AMR provides **three interfaces**: a Python API, a CLI tool, and a web UI.

### 1. Python API

```python
from accessible_math_reader import MathReader

reader = MathReader()

# ── Speech ──────────────────────────────────────────
speech = reader.to_speech(r"\frac{a}{b}")
print(speech)
# → "start fraction a over b end fraction"

# ── Braille (Nemeth) ────────────────────────────────
braille = reader.to_braille(r"\frac{a}{b}", notation="nemeth")
print(braille)
# → "⠹⠁⠌⠃⠼"

# ── Braille (UEB) ──────────────────────────────────
ueb = reader.to_braille(r"\frac{a}{b}", notation="ueb")

# ── Audio file ──────────────────────────────────────
reader.to_audio(r"\frac{a}{b}", "output.mp3")

# ── SSML markup ─────────────────────────────────────
ssml = reader.to_ssml(r"\sqrt{x}")

# ── Semantic tree inspection ────────────────────────
structure = reader.get_structure(r"\frac{a+b}{c}")

# ── Plaintext / Unicode math ────────────────────────
speech = reader.to_speech("x² + y² = z²")
speech = reader.to_speech("(a+b)/(c-d)")
speech = reader.to_speech("sqrt(x) + π")
```

#### Changing Verbosity

```python
from accessible_math_reader import MathReader, VerbosityLevel

reader = MathReader()

reader.set_verbosity(VerbosityLevel.VERBOSE)
reader.to_speech(r"\frac{a}{b}")   # "start fraction a over b end fraction"

reader.set_verbosity(VerbosityLevel.CONCISE)
reader.to_speech(r"\frac{a}{b}")   # "a over b"

reader.set_verbosity(VerbosityLevel.SUPERBRIEF)
reader.to_speech(r"\frac{a}{b}")   # "fraction a b"
```

#### Custom Configuration

```python
from accessible_math_reader import MathReader, Config
from accessible_math_reader.config import SpeechConfig, BrailleConfig, SpeechStyle, BrailleNotation

config = Config(
    speech=SpeechConfig(style=SpeechStyle.CONCISE, language="en", rate=0.9),
    braille=BrailleConfig(notation=BrailleNotation.UEB),
)

reader = MathReader(config)
```

#### Step-by-Step Navigation

```python
nav = reader.get_navigator(r"\frac{a+b}{c}")
nav.enter()       # Drill into the fraction
nav.next()        # Move to the next sibling
nav.exit()        # Go back up to the parent
path = nav.get_path()  # Breadcrumb trail from root
```

---

### 2. Command-Line Interface (`amr`)

After installing the package, the `amr` command is available system-wide.

```bash
# Speech output (default)
amr "\frac{a^2 + b^2}{c}"

# Plaintext / Unicode math
amr "x² + y² = z²"
amr "(a+b)/(c-d)"
amr "sqrt(x) + π"

# Braille output (Nemeth)
amr --braille "\frac{a}{b}"

# Braille output (UEB)
amr --braille --notation ueb "\sqrt{x}"

# Generate audio file
amr --audio output.mp3 "\frac{1}{2}"

# SSML output
amr --ssml "\frac{a}{b}"

# JSON output (speech + braille + structure)
amr --json "\frac{a}{b}"

# Show expression tree structure
amr --structure "\frac{a+b}{c}"

# Set verbosity
amr --verbosity concise "x^2 + y^2 = z^2"

# Read from file (one expression per line)
amr --input equations.txt

# Write output to file
amr --output results.txt "\frac{a}{b}"

# Interactive REPL mode
amr --interactive
```

#### Interactive Mode Commands

| Command | Action |
|---|---|
| `:quit` / `:exit` | Exit interactive mode |
| `:verbosity <level>` | Set verbosity (verbose, concise, superbrief) |
| `:braille` | Switch to Braille output |
| `:speech` | Switch to speech output |
| `:help` | Show all commands |

---

### 3. Web Interface

The web UI provides a visual, accessible interface built with Flask:

```bash
# Install web dependencies
pip install -e ".[web]"

# Development mode (with auto-reload)
python app.py
# Open http://localhost:5000

# Production mode (via the unified WSGI server)
python -m accessible_math_reader.server
# Open http://localhost:5000

# Production with Gunicorn (Linux/macOS)
gunicorn "accessible_math_reader.server:create_app()" -b 0.0.0.0:8000

# Production with Waitress (Windows)
waitress-serve --port=8000 --call accessible_math_reader.server:create_app
```

**Web UI Features:**
- LaTeX / MathML / plaintext/Unicode input with live conversion
- Tabbed output: Formula preview, Speech text, Braille, Accessible ARIA view
- Multi-format clipboard (copy as LaTeX, plain text, or Braille)
- Dark / Light / High-Contrast themes
- Full keyboard navigation (`Ctrl+Enter` to convert, `Alt+1–4` to switch tabs)
- Screen-reader optimized with ARIA live regions

---

## ⚙️ Configuration

AMR supports three configuration methods (highest priority first):

### 1. Environment Variables

```bash
# Linux / macOS
export AMR_SPEECH_STYLE=concise        # verbose | concise | superbrief
export AMR_BRAILLE_NOTATION=nemeth     # nemeth | ueb
export AMR_SPEECH_LANGUAGE=en          # Language code
export AMR_PLUGIN_DIRS=/path/to/plugins

# Windows PowerShell
$env:AMR_SPEECH_STYLE = "concise"
$env:AMR_BRAILLE_NOTATION = "ueb"
```

### 2. JSON Config File

```json
{
  "speech": {
    "style": "verbose",
    "language": "en",
    "rate": 1.0,
    "announce_structure": true
  },
  "braille": {
    "notation": "nemeth",
    "include_indicators": true
  },
  "accessibility": {
    "step_by_step": true,
    "announce_errors": true,
    "highlight_current": true
  }
}
```

```python
config = Config.from_file("amr-config.json")
reader = MathReader(config)
```

### 3. Python API

```python
config = Config()
config.speech.style = SpeechStyle.CONCISE
config.save("my-config.json")
```

> 📖 Full configuration reference: [docs/configuration.md](docs/configuration.md)

---

## 🔌 Plugin System

AMR's plugin architecture supports four extension points:

| Plugin Type | Base Class | Purpose |
|---|---|---|
| **Speech Rules** | `SpeechRulesPlugin` | Custom verbalization rules for math constructs |
| **Braille Notation** | `BrailleNotationPlugin` | Additional Braille systems (French, German, etc.) |
| **Input Format** | `InputFormatPlugin` | New input parsers (AsciiMath, MathJSON, etc.) |
| **Localization** | `BasePlugin` | Language/locale-specific adaptations |

```python
from accessible_math_reader.plugins.base import SpeechRulesPlugin, PluginInfo, PluginType

class MyCustomRules(SpeechRulesPlugin):
    @property
    def info(self):
        return PluginInfo(
            name="my-rules",
            version="1.0.0",
            description="Custom speech rules",
            author="Your Name",
            plugin_type=PluginType.SPEECH_RULES,
        )

    def get_speech_rules(self):
        return {"FRACTION": lambda node: "custom fraction rendering"}
```

---

## 📚 Documentation

| Document | Description |
|---|---|
| [API Reference](docs/api.md) | Full Python API with code examples |
| [Input Formats](docs/input-formats.md) | Supported LaTeX commands and MathML elements |
| [Accessibility Guide](docs/accessibility.md) | Screen reader, Braille display, and ARIA features |
| [Configuration](docs/configuration.md) | All speech, Braille, and accessibility settings |
| [Examples](docs/examples.md) | Common use cases, batch processing, and web integration |

### Generating Documentation Locally

This project uses [MkDocs](https://www.mkdocs.org/) with the Material theme for documentation hosting:

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Serve docs locally (live reload)
mkdocs serve

# Build static site
mkdocs build
```

> See [mkdocs.yml](mkdocs.yml) for the full configuration.

---

## 🎯 Accessibility Compliance

| Standard | Status |
|---|---|
| **WCAG 2.2 AA** | ✅ Full compliance for web interface |
| **WAI-ARIA 1.2** | ✅ Proper roles, labels, live regions, roving tabindex |
| **Screen Readers** | ✅ Tested with NVDA, JAWS, VoiceOver, Narrator |
| **Keyboard Navigation** | ✅ Full keyboard access, visible focus indicators |
| **Braille Displays** | ✅ Unicode Braille output compatible with refreshable displays |

---

## 🧑‍💻 Development

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
git clone https://github.com/AndyFerns/Accessible-Math-Reader.git
cd Accessible-Math-Reader

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -e ".[dev,web]"
```

### Running Tests

```bash
# Run full test suite with coverage
pytest tests/ -v --cov=accessible_math_reader --cov-report=term-missing

# Run a specific test file
pytest tests/test_parser.py -v
```

### Linting

```bash
# Run ruff linter
ruff check accessible_math_reader/

# Auto-fix lint issues
ruff check accessible_math_reader/ --fix
```

### Running the Web Server

```bash
# Development mode (with auto-reload on http://localhost:5000)
python app.py

# Production mode (unified WSGI server on http://localhost:5000)
python -m accessible_math_reader.server
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Install dev dependencies**: `pip install -e ".[dev]"`
4. **Make your changes** and add tests
5. **Run the linter**: `ruff check accessible_math_reader/`
6. **Run the tests**: `pytest tests/ -v`
7. **Commit** with a descriptive message
8. **Push** to your fork and open a **Pull Request**

### Areas Where Help Is Needed

- 🌍 **Localization**: Speech rules for other languages
- ⠿ **Braille**: Additional Braille notation systems (French, German, etc.)
- 🧪 **Testing**: More unit tests, especially for edge-case math expressions
- ♿ **User Testing**: Feedback from blind and low-vision users
- 📝 **Documentation**: Tutorials, guides, and examples

---

## 📦 Releasing as a Package

### Building the Distribution

```bash
# Install build tool
pip install build

# Build source distribution and wheel
python -m build

# Output will be in dist/
#   dist/accessible_math_reader-0.5.2.tar.gz
#   dist/accessible_math_reader-0.5.2-py3-none-any.whl
```

### Publishing to PyPI

```bash
# Install twine
pip install twine

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

### Installing from the Built Package

```bash
# From the wheel file
pip install dist/accessible_math_reader-0.1.0-py3-none-any.whl

# From TestPyPI
pip install --index-url https://test.pypi.org/simple/ accessible-math-reader

# From PyPI (once published)
pip install accessible-math-reader
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [gTTS](https://gtts.readthedocs.io/) — Google Text-to-Speech engine
- [lxml](https://lxml.de/) — XML/MathML parsing
- [Flask](https://flask.palletsprojects.com/) — Web framework
- [WCAG](https://www.w3.org/WAI/standards-guidelines/wcag/) — Accessibility guidelines
- [Nemeth Braille Code](https://en.wikipedia.org/wiki/Nemeth_Braille) — Mathematical Braille standard
- [UEB](https://www.uebonline.org/) — Unified English Braille
- [FCRIT](https://fcrit.ac.in/) - Fr. Conceicao Rodrigues Institute of Technology

---

<p align="center">
  Built with ♿ accessibility as a first-class priority.
</p>
