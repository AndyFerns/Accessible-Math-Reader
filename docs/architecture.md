# Architecture

> System design and module overview for the Accessible Math Reader.

---

## High-Level Pipeline

Every math expression flows through a three-stage pipeline:

```
Input (LaTeX / MathML)
        │
        ▼
  ┌───────────┐
  │   Parser   │   MathParser.parse()
  │ (core/     │   • Auto-detects LaTeX vs MathML
  │  parser.py)│   • Tokenizes and parses to AST
  └─────┬─────┘
        │ SemanticNode tree
        ▼
  ┌───────────┐
  │ Semantic   │   SemanticNode, NodeType
  │    AST     │   • Format-agnostic representation
  │ (core/     │   • Tree traversal, serialization
  │  semantic  │   • Accessibility metadata
  │  .py)      │   • MathNavigator for exploration
  └─────┬─────┘
        │
        ▼
  ┌───────────────────────────────────┐
  │           Renderers               │
  │  ┌─────────┬──────────┬────────┐  │
  │  │ Speech  │ Braille  │  ARIA  │  │
  │  │ rules.py│nemeth.py │aria_   │  │
  │  │         │ ueb.py   │renderer│  │
  │  └─────────┴──────────┴────────┘  │
  └───────────────────────────────────┘
        │
        ▼
  Output (text, Braille, audio, HTML)
```

## Module Breakdown

### Core (`accessible_math_reader/core/`)

| Module | Responsibility |
|---|---|
| `parser.py` | `MathParser` — Parses LaTeX and MathML into `SemanticNode` trees. Handles fractions, exponents, subscripts, roots, summations, integrals, Greek letters, and more. |
| `semantic.py` | `SemanticNode`, `NodeType`, `MathNavigator` — The format-agnostic AST. Nodes carry type, content, children, parent references, and accessibility metadata. |
| `renderer.py` | `BaseRenderer` (ABC), `MathRenderer` — Dispatches rendering to speech or Braille converters. |
| `aria_navigator.py` | `ARIANavigator`, `FocusManager` — ARIA-enhanced navigation with Browse / Explore / Verbose Learning modes, roving tabindex, and screen reader announcements. |
| `aria_renderer.py` | `render_to_aria_html()` — Generates semantic HTML with ARIA roles, labels, tabindex, and live regions. |
| `accessibility_contract.py` | `AccessibilityContract` — Validation protocols ensuring ARIA compliance and deterministic IDs. |

### Speech (`accessible_math_reader/speech/`)

| Module | Responsibility |
|---|---|
| `engine.py` | `SpeechEngine`, `TTSBackend`, `GTTSBackend` — TTS abstraction with gTTS as default. Supports SSML generation and custom backends. |
| `rules.py` | `SpeechRenderer`, `SpeechRuleSet`, `VerbosityLevel` — Verbosity-aware speech rendering. Maps each `NodeType` to a natural language phrase. |

### Braille (`accessible_math_reader/braille/`)

| Module | Responsibility |
|---|---|
| `nemeth.py` | `NemethConverter` — Full Nemeth Braille Code implementation: numeric indicators, letter signs, fraction/superscript/subscript/radical notation. |
| `ueb.py` | `UEBConverter` — Unified English Braille technical notation with its own indicator and grouping conventions. |

### Plugins (`accessible_math_reader/plugins/`)

| Module | Responsibility |
|---|---|
| `base.py` | `BasePlugin`, `SpeechRulesPlugin`, `BrailleNotationPlugin`, `InputFormatPlugin`, `PluginManager` — Abstract base classes and a dynamic loader for extending AMR at runtime. |

### Top-Level Package Files

| File | Responsibility |
|---|---|
| `__init__.py` | Public API surface — exports `MathReader`, `MathParser`, `Config`, converters, etc. |
| `reader.py` | `MathReader` — The unified, high-level API that ties parsing, rendering, and synthesis together. |
| `cli.py` | `amr` CLI — argparse-based command-line tool with interactive and batch modes. |
| `config.py` | `Config`, `SpeechConfig`, `BrailleConfig`, `AccessibilityConfig` — Dataclass-based configuration with JSON file and env-var loading. |

### Web Application

| File | Responsibility |
|---|---|
| `app.py` | Flask entry point — routes for `/` and `/convert`. |
| `src/latex_parser.py` | Legacy regex-based LaTeX parser for the web route. |
| `src/braille_converter.py` | Simple character-level Braille mapper for the web route. |
| `src/speech_converter.py` | gTTS wrapper for the web route. |
| `templates/index.html` | Full-featured, accessible web UI. |
| `static/js/app.js` | Frontend JS — tabs, keyboard shortcuts, theme toggler. |
| `static/js/clipboard.js` | Multi-format copy-to-clipboard module. |
| `static/css/style.css` | Responsive stylesheet with dark/light/high-contrast modes. |

## Design Decisions

1. **Semantic AST as the pivot format** — All input formats parse to the same `SemanticNode` tree, making it trivial to add new input formats or output renderers without coupling.

2. **Doxygen-style docstrings** — The project uses `@brief`, `@param`, `@return` docstrings for compatibility with Doxygen and for clear structured documentation.

3. **Plugin architecture** — Speech rules, Braille notations, and input formats can be extended without modifying core code.

4. **Dual web stacks** — The `src/` directory contains the original Flask helpers (simple regex parser), while `accessible_math_reader/` is the refactored, modular package. The web UI uses `src/` for its routes; the package API uses the `core/` modules.
