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

# Convert plaintext / Unicode math to spoken English
speech = reader.to_speech("x² + y² = z²")
print(speech)
# → "x to the power of 2 plus y to the power of 2 equals z to the power of 2"

speech = reader.to_speech("(a+b)/(c-d)")
print(speech)
# → "(a plus b) divided by (c minus d)"

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

# Plaintext input
amr "x² + y² = z²"
amr "(a+b)/(c-d)"

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

Type a LaTeX expression like `\frac{a}{b}`, a plaintext expression like `x² + y²`, or paste math from any document and click **Convert** to see speech, Braille, and accessible HTML output.

## What's Next?

- Learn about [all supported LaTeX, MathML, and plaintext syntax](../input-formats.md)
- Explore the full [Python API](../api.md)
- Customize output with the [Configuration guide](../configuration.md)
- See more [code examples](../examples.md)
