# Examples

> Common use cases and code samples for Accessible Math Reader.

---

## Basic Usage

### Simple Fraction

```python
from accessible_math_reader import MathReader

reader = MathReader()

# Convert to speech
speech = reader.to_speech(r"\frac{1}{2}")
print(speech)
# Output: "start fraction 1 over 2 end fraction"

# Convert to Braille
braille = reader.to_braille(r"\frac{1}{2}")
print(braille)
# Output: "⠹⠂⠌⠆⠼"
```

### Quadratic Formula

```python
latex = r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"

speech = reader.to_speech(latex)
print(speech)
# "x equals start fraction negative b plus or minus 
#  square root of b squared minus 4 a c end square root 
#  over 2 a end fraction"
```

---

## Working with the Semantic Tree

### Inspecting Structure

```python
from accessible_math_reader import MathParser, NodeType

parser = MathParser()
tree = parser.parse(r"\frac{a+b}{c}")

# Print tree structure
def print_tree(node, depth=0):
    indent = "  " * depth
    print(f"{indent}{node.node_type.name}: {node.content or ''}")
    for child in node.children:
        print_tree(child, depth + 1)

print_tree(tree)
# ROOT:
#   FRACTION:
#     GROUP:
#       IDENTIFIER: a
#       OPERATOR: +
#       IDENTIFIER: b
#     IDENTIFIER: c
```

### Traversing Nodes

```python
for node in tree.walk():
    if node.node_type == NodeType.IDENTIFIER:
        print(f"Found variable: {node.content}")
```

---

## Speech Options

### Different Verbosity Levels

```python
from accessible_math_reader import VerbosityLevel

latex = r"\frac{a}{b}"

reader.set_verbosity(VerbosityLevel.VERBOSE)
print(reader.to_speech(latex))
# "start fraction a over b end fraction"

reader.set_verbosity(VerbosityLevel.CONCISE)
print(reader.to_speech(latex))
# "a over b"

reader.set_verbosity(VerbosityLevel.SUPERBRIEF)
print(reader.to_speech(latex))
# "fraction a b"
```

### Generating Audio Files

```python
# MP3 output
reader.to_audio(
    r"\int_0^\infty e^{-x} dx",
    "integral.mp3"
)

# Get SSML for custom TTS
ssml = reader.to_ssml(r"\sqrt{x}")
print(ssml)
# <speak><prosody rate="90%">square root of <break time="200ms"/>x</prosody></speak>
```

---

## Braille Conversion

### Nemeth vs UEB

```python
latex = r"x^2 + y^2 = r^2"

# Nemeth (North America standard)
nemeth = reader.to_braille(latex, notation="nemeth")
print(f"Nemeth: {nemeth}")

# UEB (International standard)
ueb = reader.to_braille(latex, notation="ueb")
print(f"UEB: {ueb}")
```

### Exporting to BRF File

```python
braille = reader.to_braille(
    r"\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}"
)

with open("summation.brf", "w", encoding="utf-8") as f:
    f.write(braille)
```

---

## Interactive Navigation

### Step-by-Step Exploration

```python
nav = reader.get_navigator(r"\frac{a+b}{c}")

# Start at root
print(nav.get_current_speech())  # "fraction"

# Enter fraction
nav.enter()
print(nav.get_current_speech())  # "numerator: a plus b"

# Move to sibling (denominator)
nav.next()
print(nav.get_current_speech())  # "denominator: c"

# Go back up
nav.exit()
print(nav.get_current_speech())  # "fraction"
```

### Where Am I?

```python
path = nav.get_context()
print(path)
# ["root", "fraction", "numerator"]
```

---

## Batch Processing

### Processing Multiple Expressions

```python
expressions = [
    r"\frac{1}{2}",
    r"\sqrt{x^2 + y^2}",
    r"\sum_{i=1}^{n} i",
]

results = []
for expr in expressions:
    results.append({
        "latex": expr,
        "speech": reader.to_speech(expr),
        "braille": reader.to_braille(expr)
    })

# Export as JSON
import json
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Reading from File

```python
with open("equations.txt") as f:
    for line in f:
        latex = line.strip()
        if latex:
            print(f"{latex} → {reader.to_speech(latex)}")
```

---

## Web Integration

### Flask Endpoint

```python
from flask import Flask, request, jsonify
from accessible_math_reader import MathReader

app = Flask(__name__)
reader = MathReader()

@app.route("/api/convert", methods=["POST"])
def convert():
    latex = request.json.get("latex", "")
    return jsonify({
        "speech": reader.to_speech(latex),
        "braille": reader.to_braille(latex),
    })
```

### JavaScript Fetch

```javascript
async function convertMath(latex) {
    const response = await fetch('/api/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latex })
    });
    return response.json();
}

const result = await convertMath('\\frac{a}{b}');
console.log(result.speech);  // "start fraction a over b end fraction"
```

---

## Error Handling

### Parsing Errors

```python
from accessible_math_reader.core.parser import ParseError

try:
    tree = parser.parse(r"\frac{a}")  # Missing argument
except ParseError as e:
    print(f"Error: {e.message}")
    print(f"At position: {e.position}")
```

### Validation

```python
def validate_latex(latex: str) -> bool:
    try:
        parser.parse(latex)
        return True
    except ParseError:
        return False
```

---

## Custom Configuration

### Per-Request Settings

```python
from accessible_math_reader import Config
from accessible_math_reader.config import SpeechConfig, SpeechStyle

# Create a custom config for this request
config = Config(speech=SpeechConfig(style=SpeechStyle.CONCISE))
reader = MathReader(config)

speech = reader.to_speech(r"\frac{a}{b}")
# "a over b" (concise output)
```

### Environment-Based Config

```python
import os

os.environ["AMR_SPEECH_STYLE"] = "superbrief"
config = Config.from_env()
reader = MathReader(config)
```
