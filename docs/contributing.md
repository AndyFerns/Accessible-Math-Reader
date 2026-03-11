# Contributing

Thank you for your interest in contributing to Accessible Math Reader! This guide will help you get started.

## Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/Accessible-Math-Reader.git
cd Accessible-Math-Reader

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev,web]"
```

## Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes.
3. Run linting:
   ```bash
   ruff check accessible_math_reader/
   ```
4. Run tests:
   ```bash
   pytest tests/ -v
   ```
5. Commit with a descriptive message.
6. Push and open a Pull Request.

## Code Style

- **Linter**: [Ruff](https://docs.astral.sh/ruff/) (configured in `pyproject.toml`)
- **Docstrings**: Doxygen-style (`@brief`, `@param`, `@return`)
- **Type hints**: Required for all public functions
- **Line length**: 100 characters max

## What to Work On

| Area | Description |
|---|---|
| 🌍 Localization | Speech rules for languages other than English |
| ⠿ Braille | Plugins for French, German, or other Braille math notations |
| 🧪 Testing | Unit tests — especially for edge-case LaTeX expressions |
| ♿ User Testing | Feedback from blind and low-vision users |
| 📝 Documentation | Tutorials, guides, videos |
| 🔌 Plugins | AsciiMath parser, custom TTS backends, etc. |

## Reporting Issues

Please open an issue on GitHub with:

- A clear title and description
- Steps to reproduce (if it's a bug)
- Expected vs actual behavior
- Python version and OS

## Code of Conduct

Be respectful and constructive. We are building a tool for accessibility — inclusion applies to our community too.
