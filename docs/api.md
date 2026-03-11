# Accessible Math Reader - API Reference

> Complete Python API documentation for the Accessible Math Reader package.

---

## Table of Contents

- [MathReader](#mathreader) - High-level API
- [MathParser](#mathparser) - Parsing LaTeX/MathML/Plaintext
- [SemanticNode](#semanticnode) - Abstract Syntax Tree
- [SpeechEngine](#speechengine) - Text-to-Speech
- [NemethConverter](#nemethconverter) - Nemeth Braille
- [UEBConverter](#uebconverter) - UEB Braille
- [Config](#config) - Configuration

---

## MathReader

Primary user-facing class that combines parsing, speech, and Braille conversion.

### Import

```python
from accessible_math_reader import MathReader
```

### Constructor

```python
MathReader(config: Optional[Config] = None)
```

**Parameters:**
- `config` - Optional configuration object. Uses defaults if None.

### Methods

#### `parse(math_input: str) → SemanticNode`

Parse mathematical input to a semantic tree.

```python
reader = MathReader()
tree = reader.parse(r"\frac{a}{b}")
print(tree.node_type)  # NodeType.ROOT
```

#### `to_speech(math_input: str) → str`

Convert mathematical input to speech text.

```python
speech = reader.to_speech(r"\frac{a}{b}")
# Output: "start fraction a over b end fraction"
```

#### `to_braille(math_input: str, notation: str = "nemeth") → str`

Convert mathematical input to Braille.

```python
braille = reader.to_braille(r"\frac{a}{b}", notation="nemeth")
# Output: "⠹⠁⠌⠃⠼"
```

**Parameters:**
- `notation` - `"nemeth"` or `"ueb"`

#### `to_audio(math_input: str, output_path: str = "output.mp3") → Path`

Generate audio file from mathematical input.

```python
path = reader.to_audio(r"\frac{a}{b}", "fraction.mp3")
```

#### `to_ssml(math_input: str) → str`

Generate SSML markup with math-appropriate prosody.

```python
ssml = reader.to_ssml(r"\frac{a}{b}")
```

#### `get_navigator(math_input: str) → MathNavigator`

Get a navigator for step-by-step exploration.

```python
nav = reader.get_navigator(r"\frac{a+b}{c}")
nav.enter()  # Move into first child
print(nav.get_current_speech())
```

#### `set_verbosity(level: str | VerbosityLevel)`

Change speech verbosity level.

```python
reader.set_verbosity("concise")
# Or: reader.set_verbosity(VerbosityLevel.CONCISE)
```

---

## MathParser

Low-level parser for LaTeX, MathML, and plaintext/Unicode input.

### Import

```python
from accessible_math_reader import MathParser
from accessible_math_reader.core.parser import ParseError
```

### Methods

#### `parse(input_str: str) → SemanticNode`

Auto-detect input format and parse.

```python
parser = MathParser()

# LaTeX (auto-detected)
tree = parser.parse(r"\sqrt{x}")

# MathML (auto-detected)
tree = parser.parse('<math><mi>x</mi></math>')

# Plaintext (auto-detected)
tree = parser.parse("x² + y² = z²")
tree = parser.parse("(a+b)/(c-d)")
```

#### `parse_latex(latex: str) → SemanticNode`

Parse LaTeX string specifically.

```python
tree = parser.parse_latex(r"\int_0^\infty e^{-x} dx")
```

#### `parse_mathml(mathml: str) → SemanticNode`

Parse MathML string specifically.

```python
mathml = '<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>'
tree = parser.parse_mathml(mathml)
```

#### `parse_plaintext(text: str) → SemanticNode`

Parse a plaintext / Unicode math string specifically.

Handles: `a/b`, `x^2`, `x**2`, `x²`, `x₁`, `sqrt(x)`, `√x`,
Unicode Greek (`π α Σ`), Unicode operators (`× ÷ ± ≤ ≥ ≠`),
and named functions (`sin`, `cos`, `log`, etc.).

```python
tree = parser.parse_plaintext("sqrt(x² + y²) + π")
```

### Import

```python
from accessible_math_reader import MathParser
from accessible_math_reader.core.parser import ParseError
```

### Methods

#### `parse(input_str: str) → SemanticNode`

Auto-detect input format and parse.

```python
parser = MathParser()
tree = parser.parse(r"\sqrt{x}")
```

#### `parse_latex(latex: str) → SemanticNode`

Parse LaTeX string specifically.

```python
tree = parser.parse_latex(r"\int_0^\infty e^{-x} dx")
```

#### `parse_mathml(mathml: str) → SemanticNode`

Parse MathML string specifically.

```python
mathml = '<math><mfrac><mi>a</mi><mi>b</mi></mfrac></math>'
tree = parser.parse_mathml(mathml)
```

### Exceptions

#### `ParseError`

Raised when parsing fails.

```python
try:
    tree = parser.parse(r"\frac{a}")  # Missing denominator
except ParseError as e:
    print(f"Parse failed: {e.message}")
    print(f"Position: {e.position}")
```

---

## SemanticNode

Represents a node in the mathematical expression tree.

### Import

```python
from accessible_math_reader import SemanticNode, NodeType
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `node_id` | `str` | Unique identifier |
| `node_type` | `NodeType` | Type of mathematical construct |
| `content` | `str` | Text content (for leaf nodes) |
| `children` | `list[SemanticNode]` | Child nodes |
| `parent` | `SemanticNode \| None` | Parent node |

### NodeType Enum

```python
class NodeType(Enum):
    ROOT = auto()
    GROUP = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    FRACTION = auto()
    SUPERSCRIPT = auto()
    SUBSCRIPT = auto()
    SQRT = auto()
    NROOT = auto()
    OPERATOR = auto()
    RELATION = auto()
    FUNCTION = auto()
    SUM = auto()
    PRODUCT = auto()
    INTEGRAL = auto()
    LIMIT = auto()
    MATRIX = auto()
    MATRIX_ROW = auto()
    TEXT = auto()
    SPACE = auto()
```

### Methods

#### `walk() → Iterator[SemanticNode]`

Depth-first traversal of the subtree.

```python
for node in tree.walk():
    print(f"{node.node_type}: {node.content}")
```

#### `to_dict() → dict`

Serialize to dictionary (for JSON).

```python
data = tree.to_dict()
json.dumps(data)
```

#### `from_dict(data: dict) → SemanticNode`

Deserialize from dictionary.

```python
tree = SemanticNode.from_dict(data)
```

#### `get_aria_attributes() → dict`

Get ARIA attributes for accessible HTML rendering.

```python
attrs = node.get_aria_attributes()
# {'role': 'group', 'aria-label': 'fraction', ...}
```

---

## SpeechEngine

Text-to-speech engine abstraction.

### Import

```python
from accessible_math_reader import SpeechEngine
```

### Methods

#### `synthesize(text: str, output_path: str) → Path`

Synthesize text to audio file.

```python
engine = SpeechEngine()
path = engine.synthesize("a divided by b", "speech.mp3")
```

#### `to_ssml(text: str, rate: float, pitch: str) → str`

Generate SSML markup.

```python
ssml = engine.to_ssml("a over b", rate=0.9, pitch="medium")
```

#### `to_math_ssml(text: str) → str`

Generate math-optimized SSML with pauses.

```python
ssml = engine.to_math_ssml("start fraction a over b end fraction")
```

---

## NemethConverter

Converts semantic trees to Nemeth Braille Code.

### Import

```python
from accessible_math_reader import NemethConverter
```

### Usage

```python
from accessible_math_reader import MathParser, NemethConverter

parser = MathParser()
tree = parser.parse(r"\frac{1}{2}")

converter = NemethConverter()
braille = converter.render(tree)
print(braille)  # ⠹⠂⠌⠆⠼
```

---

## UEBConverter

Converts semantic trees to Unified English Braille.

### Import

```python
from accessible_math_reader import UEBConverter
```

### Usage

```python
from accessible_math_reader import MathParser, UEBConverter

parser = MathParser()
tree = parser.parse(r"x^2")

converter = UEBConverter()
braille = converter.render(tree)
```

---

## Config

Configuration management for the package.

### Import

```python
from accessible_math_reader import Config
from accessible_math_reader.config import (
    SpeechConfig, 
    BrailleConfig,
    AccessibilityConfig,
    SpeechStyle,
    BrailleNotation
)
```

### Creating Configuration

```python
config = Config(
    speech=SpeechConfig(
        style=SpeechStyle.CONCISE,
        language="en",
        rate=0.9
    ),
    braille=BrailleConfig(
        notation=BrailleNotation.NEMETH
    )
)

reader = MathReader(config)
```

### Loading from File

```python
config = Config.from_file("amr-config.json")
```

### Loading from Environment

```python
config = Config.from_env()
# Reads AMR_SPEECH_STYLE, AMR_BRAILLE_NOTATION, etc.
```

### Saving Configuration

```python
config.save("my-config.json")
```

---

## VerbosityLevel

Speech verbosity options.

```python
from accessible_math_reader import VerbosityLevel

class VerbosityLevel(Enum):
    VERBOSE = "verbose"      # "start fraction a over b end fraction"
    CONCISE = "concise"      # "a over b"
    SUPERBRIEF = "superbrief"  # "fraction a b"
```
