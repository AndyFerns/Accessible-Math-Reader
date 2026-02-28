# Installation

## Requirements

- **Python 3.9** or higher
- **pip** package manager
- **Internet connection** (required for gTTS audio generation)

## Install as a Python Package

### 1. Clone the Repository

```bash
git clone https://github.com/AndyFerns/Accessible-Math-Reader.git
cd Accessible-Math-Reader
```

### 2. Create a Virtual Environment

=== "Windows"

    ```powershell
    python -m venv venv
    venv\Scripts\activate
    ```

=== "Linux / macOS"

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

### 3. Install the Package

Choose the extras you need:

```bash
# Full install (library + dev tools + web UI)
pip install -e ".[dev,web]"

# Library only (minimal)
pip install -e .

# Library + web UI
pip install -e ".[web]"
```

### 4. Verify Installation

```bash
# Check the CLI is available
amr --version

# Quick test
amr "\frac{a}{b}"
```

## Install from PyPI *(coming soon)*

```bash
pip install accessible-math-reader
```

## Dependencies

| Package | Purpose | Required |
|---|---|---|
| `gtts >= 2.5.0` | Google Text-to-Speech | ✅ Core |
| `lxml >= 4.9.0` | XML/MathML parsing | ✅ Core |
| `flask >= 3.0.0` | Web interface | Optional (`[web]`) |
| `pytest >= 7.0.0` | Testing | Optional (`[dev]`) |
| `ruff >= 0.1.0` | Linting | Optional (`[dev]`) |

## Uninstalling

```bash
pip uninstall accessible-math-reader
```
