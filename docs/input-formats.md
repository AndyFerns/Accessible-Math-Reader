# Supported Input Formats

> Guide to LaTeX and MathML syntax supported by Accessible Math Reader.

---

## LaTeX Input

### Basic Syntax

| Expression | LaTeX | Speech Output |
|------------|-------|---------------|
| Fraction | `\frac{a}{b}` | "start fraction a over b end fraction" |
| Superscript | `x^2` | "x to the power of 2" |
| Subscript | `x_i` | "x sub i" |
| Square Root | `\sqrt{x}` | "square root of x" |
| nth Root | `\sqrt[n]{x}` | "nth root of x" |

### Greek Letters

| Letter | LaTeX | Letter | LaTeX |
|--------|-------|--------|-------|
| α | `\alpha` | π | `\pi` |
| β | `\beta` | σ | `\sigma` |
| γ | `\gamma` | θ | `\theta` |
| δ | `\delta` | ω | `\omega` |
| ε | `\epsilon` | λ | `\lambda` |
| Δ | `\Delta` | Σ | `\Sigma` |
| Π | `\Pi` | Ω | `\Omega` |

### Operators and Relations

| Symbol | LaTeX | Symbol | LaTeX |
|--------|-------|--------|-------|
| + | `+` | = | `=` |
| - | `-` | ≠ | `\neq` |
| × | `\times` | < | `<` |
| ÷ | `\div` | > | `>` |
| ± | `\pm` | ≤ | `\leq` |
| ∓ | `\mp` | ≥ | `\geq` |

### Advanced Constructs

#### Summation

```latex
\sum_{i=1}^{n} x_i
```
**Speech:** "summation from i equals 1 to n of x sub i"

#### Product

```latex
\prod_{i=1}^{n} x_i
```
**Speech:** "product from i equals 1 to n of x sub i"

#### Integral

```latex
\int_0^\infty e^{-x^2} dx
```
**Speech:** "integral from 0 to infinity of e to the power of negative x squared d x"

#### Limit

```latex
\lim_{x \to 0} \frac{\sin x}{x}
```
**Speech:** "limit as x approaches 0 of start fraction sine of x over x end fraction"

#### Matrix

```latex
\begin{pmatrix} a & b \\ c & d \end{pmatrix}
```
**Speech:** "2 by 2 matrix, row 1: a, b; row 2: c, d"

### Functions

| Function | LaTeX | Speech Output |
|----------|-------|---------------|
| sin | `\sin x` | "sine of x" |
| cos | `\cos x` | "cosine of x" |
| tan | `\tan x` | "tangent of x" |
| log | `\log x` | "logarithm of x" |
| ln | `\ln x` | "natural log of x" |
| exp | `\exp x` | "exponential of x" |

---

## MathML Input

The parser supports both content and presentation MathML.

### Example: Fraction

```xml
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac>
    <mi>a</mi>
    <mi>b</mi>
  </mfrac>
</math>
```

### Supported Elements

| Element | Purpose |
|---------|---------|
| `<mfrac>` | Fractions |
| `<msup>` | Superscripts |
| `<msub>` | Subscripts |
| `<msqrt>` | Square roots |
| `<mroot>` | Nth roots |
| `<mrow>` | Grouping |
| `<mi>` | Identifiers |
| `<mn>` | Numbers |
| `<mo>` | Operators |
| `<mtext>` | Text |

---

## Auto-Detection

The parser automatically detects input format:

```python
reader = MathReader()

# Detects as LaTeX
reader.to_speech(r"\frac{a}{b}")

# Detects as MathML
reader.to_speech('<math><mi>x</mi></math>')
```

Detection rules:
1. If starts with `<math`, parse as MathML
2. Otherwise, parse as LaTeX

---

## Error Handling

```python
from accessible_math_reader import MathParser
from accessible_math_reader.core.parser import ParseError

parser = MathParser()

try:
    tree = parser.parse(r"\frac{a}")  # Missing argument
except ParseError as e:
    print(f"Error: {e.message}")
    print(f"Position: {e.position}")
    # Error: Expected second argument for \frac
    # Position: 7
```
