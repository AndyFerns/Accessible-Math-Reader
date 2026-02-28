# Quick Start

Get up and running with AMR in under 2 minutes.

## Python API

```python
from accessible_math_reader import MathReader

reader = MathReader()

# Convert LaTeX to spoken English
speech = reader.to_speech(r"\frac{a}{b}")
print(speech)
# → "start fraction a over b end fraction"

# Convert to Nemeth Braille
braille = reader.to_braille(r"\frac{a}{b}")
print(braille)
# → "⠹⠁⠌⠃⠼"

# Generate an audio file
reader.to_audio(r"\sqrt{x^2 + y^2}", "pythagorean.mp3")
```

## CLI

```bash
# Speech output (default)
amr "\frac{1}{2}"

# Braille output
amr --braille "\frac{1}{2}"

# Interactive mode
amr --interactive
```

## Web Interface

```bash
python app.py
# Open http://localhost:5000 in your browser
```

Type a LaTeX expression like `\frac{a}{b}` and click **Convert** to see speech, Braille, and accessible HTML output.

## What's Next?

- Learn about [all supported LaTeX and MathML syntax](../input-formats.md)
- Explore the full [Python API](../api.md)
- Customize output with the [Configuration guide](../configuration.md)
- See more [code examples](../examples.md)
