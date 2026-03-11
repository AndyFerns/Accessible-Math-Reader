# Accessibility Guide

> Complete guide to screen reader, Braille, and ARIA accessibility features.

---

## Overview

Accessible Math Reader is designed with accessibility as a core principle:

- **Screen Reader Support**: NVDA, JAWS, VoiceOver, Narrator
- **Braille Displays**: Nemeth and UEB notation
- **Keyboard Navigation**: Full keyboard access with ARIA support
- **Visual Accessibility**: High contrast mode, zoom controls

---

## Speech Output

### Verbosity Levels

Control how much detail is spoken:

| Level | Description | Example Output |
|-------|-------------|----------------|
| **Verbose** | Full structural description | "start fraction a over b end fraction" |
| **Concise** | Shortened descriptions | "a over b" |
| **Superbrief** | Minimal output | "fraction a b" |

### Configuration

```python
from accessible_math_reader import MathReader, VerbosityLevel

reader = MathReader()
reader.set_verbosity(VerbosityLevel.CONCISE)
```

Or via environment variable:
```bash
export AMR_SPEECH_STYLE=concise
```

---

## Braille Output

### Nemeth Code

The standard for mathematics Braille in North America.

| Expression | Nemeth Braille |
|------------|----------------|
| a/b | ⠹⠁⠌⠃⠼ |
| x² | ⠭⠘⠆ |
| √x | ⠜⠭⠻ |

### UEB (Unified English Braille)

International standard for English Braille.

| Expression | UEB Braille |
|------------|-------------|
| a/b | ⠷⠁⠌⠃⠾ |
| x² | ⠭⠔⠃ |
| √x | ⠩⠭ |

### Choosing Notation

```python
# Nemeth (default)
reader.to_braille(r"\frac{a}{b}", notation="nemeth")

# UEB
reader.to_braille(r"\frac{a}{b}", notation="ueb")
```

### Refreshable Braille Display

The Unicode Braille output is compatible with refreshable Braille displays. Copy the output directly to use with your Braille hardware.

---

## Keyboard Navigation

### Web Interface Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Convert expression |
| `Ctrl + L` | Clear input |
| `Ctrl + B` | Toggle sidebar |
| `Ctrl + Shift + T` | Toggle theme |
| `Alt + 1` | Formula tab |
| `Alt + 2` | Speech tab |
| `Alt + 3` | Braille tab |
| `Alt + 4` | Accessible tab |

### ARIA Navigation (Accessible Tab)

Navigate within mathematical expressions:

| Key | Action |
|-----|--------|
| `Enter` | Drill down into element |
| `Escape` | Go up to parent |
| `←` / `→` | Move between siblings |
| `Home` | Jump to first sibling |
| `End` | Jump to last sibling |
| `Space` | Announce current position |

---

## Navigation Modes

### Browse Mode

Linear navigation through the expression.

```
"start fraction, a, over, b, end fraction"
```

### Explore Mode (Default)

Interactive exploration with drill-down.

```
"Fraction" → [Enter] → "a" → [→] → "b"
```

### Verbose Learning Mode

Extra context for learning math structure.

```
"Fraction: The numerator a is divided by the denominator b"
```

### Setting Mode

```python
reader.set_nav_mode("explore")  # or "browse", "verbose"
```

---

## Screen Reader Tips

### NVDA

1. Enable "Speak typed characters" for input feedback
2. Use browse mode (NVDA+Space) for linear reading
3. Focus mode (NVDA+Space again) for ARIA navigation

### JAWS

1. Use virtual cursor for reading formula output
2. PC cursor for ARIA navigation
3. Enable "Math processing" if available

### VoiceOver (macOS)

1. Use VO+Shift+↓ to enter web content
2. Navigate with VO+← and VO+→
3. Interact with VO+Shift+↓ for ARIA elements

### Narrator (Windows)

1. Use Scan mode (Caps+Space) for reading
2. Exit Scan mode for ARIA interaction
3. Arrow keys for navigation within math

---

## Visual Accessibility

### Color Themes

- **Dark Mode**: Reduced eye strain, high contrast text
- **Light Mode**: Traditional appearance
- **High Contrast**: Maximum visibility for low vision

### Zoom Controls

```javascript
// Web interface
zoomIn()   // +10%
zoomOut()  // -10%
resetZoom() // 100%
```

### Font Sizing

The interface respects browser font size settings.

---

## ARIA Implementation

### Live Regions

Status messages announce automatically:
```html
<div role="status" aria-live="polite">Copied to clipboard</div>
```

### Math Roles

```html
<div role="math" aria-label="a divided by b">
  ...
</div>
```

### Focus Management

Proper focus order and visible focus indicators throughout.

---

## Testing Accessibility

We test with:
- **Screen Readers**: NVDA, JAWS, VoiceOver, Narrator
- **Tools**: axe DevTools, WAVE, Lighthouse
- **Manual Testing**: Keyboard-only navigation
- **User Testing**: Feedback from blind and low-vision users
