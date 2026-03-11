# Supported Input Formats

> Guide to LaTeX, MathML, and plaintext/Unicode math syntax supported by Accessible Math Reader.

---

## Plaintext / Unicode Math Input *(NEW)*

The easiest way to enter math — just type or paste everyday notation.

### Basic Arithmetic

| Expression | Input | Speech Output |
|------------|-------|---------------|
| Addition | `a + b` | "a plus b" |
| Subtraction | `a - b` | "a minus b" |
| Multiplication | `a * b` or `a × b` | "a times b" |
| Division | `a / b` or `a ÷ b` | "a divided by b" |

### Fractions (Parenthesised Division)

| Expression | Input | Speech Output |
|------------|-------|---------------|
| Simple | `a/b` | "a divided by b" |
| Grouped | `(a+b)/(c-d)` | "(a plus b) divided by (c minus d)" |

### Exponents & Subscripts

| Expression | Input | Speech Output |
|------------|-------|---------------|
| Caret | `x^2` | "x to the power of 2" |
| Double-star | `x**2` | "x to the power of 2" |
| Unicode | `x²` | "x to the power of 2" |
| Subscript | `x_i` | "x sub i" |
| Unicode sub | `x₁` | "x sub 1" |

All Unicode superscript digits (`⁰¹²³⁴⁵⁶⁷⁸⁹`) and subscript digits (`₀₁₂₃₄₅₆₇₈₉`) are recognised.

### Square Root

| Input | Speech Output |
|-------|---------------|
| `sqrt(x)` | "square root of x" |
| `√(x)` | "square root of x" |
| `√x` | "square root of x" |

### Unicode Greek Letters

You can paste Greek characters directly:

| Character | Name | Character | Name |
|-----------|------|-----------|------|
| α | alpha | π | pi |
| β | beta | σ | sigma |
| γ | gamma | θ | theta |
| δ | delta | ω | omega |
| ε | epsilon | λ | lambda |
| Δ | Delta | Σ | Sigma |
| Π | Pi | Ω | Omega |

### Unicode Symbols

| Symbol | Input | Meaning |
|--------|-------|---------|
| ∑ | `∑` | Summation |
| ∫ | `∫` | Integral |
| ∞ | `∞` | Infinity |
| ± | `±` | Plus or minus |
| ≤ | `≤` or `<=` | Less than or equal to |
| ≥ | `≥` or `>=` | Greater than or equal to |
| ≠ | `≠` or `!=` | Not equal to |
| ≈ | `≈` | Approximately equal |

### Functions

Named math functions are recognised in plaintext:

```
sin(x)   cos(x)   tan(x)   log(x)   ln(x)   exp(x)   lim
```

### Plaintext Examples

```text
x² + y² = z²
(a + b) / (c - d)
sqrt(x² + y²) + π
sin(x) * cos(x)
∫ x² dx
∑ i = 1 + 2 + 3
```

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

# Detects as MathML
reader.to_speech('<math><mi>x</mi></math>')

# Detects as LaTeX (contains backslash commands)
reader.to_speech(r"\frac{a}{b}")

# Detects as plaintext (no backslash commands, no XML)
reader.to_speech("x² + y² = z²")
reader.to_speech("(a+b)/(c-d)")
reader.to_speech("sqrt(x) + π")
```

Detection rules (applied in order):
1. If starts with `<math` or `<?xml`, parse as **MathML**
2. If contains backslash commands (`\word`), parse as **LaTeX**
3. Otherwise, parse as **Plaintext / Unicode math**

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
