"""!
@file cli.py
@brief Command-line interface for Accessible Math Reader.

@details
Provides a CLI tool for converting mathematical notation to speech
and Braille from the command line. Supports both interactive and
batch processing modes.

@section cli_usage Usage Examples
@code{.bash}
# Convert LaTeX to speech
amr "\\frac{a}{b}"

# Convert to Braille
amr --braille "\\frac{a}{b}"

# Use concise verbosity
amr --verbosity concise "x^2 + y^2 = z^2"

# Output to file
amr --output speech.txt "\\sqrt{2}"

# Generate audio
amr --audio output.mp3 "\\frac{1}{2}"

# Read from file
amr --input equations.txt

# Interactive mode
amr --interactive
@endcode

@author Accessible Math Reader Contributors
@version 0.1.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from accessible_math_reader import __version__
from accessible_math_reader.config import Config, SpeechStyle, BrailleNotation
from accessible_math_reader.reader import MathReader
from accessible_math_reader.core.parser import ParseError


def create_parser() -> argparse.ArgumentParser:
    """!
    @brief Create the argument parser for the CLI.
    
    @return Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="amr",
        description="Accessible Math Reader - Convert math to speech and Braille",
        epilog="For more information, visit: https://github.com/accessible-math-reader",
    )
    
    parser.add_argument(
        "expression",
        nargs="?",
        help="Mathematical expression to convert (LaTeX or MathML)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    # Output format options
    output_group = parser.add_argument_group("Output Format")
    output_group.add_argument(
        "-s", "--speech",
        action="store_true",
        default=True,
        help="Output speech text (default)"
    )
    output_group.add_argument(
        "-b", "--braille",
        action="store_true",
        help="Output Braille instead of speech"
    )
    output_group.add_argument(
        "--notation",
        choices=["nemeth", "ueb"],
        default="nemeth",
        help="Braille notation to use (default: nemeth)"
    )
    output_group.add_argument(
        "--ssml",
        action="store_true",
        help="Output SSML instead of plain text"
    )
    
    # Audio options
    audio_group = parser.add_argument_group("Audio")
    audio_group.add_argument(
        "-a", "--audio",
        metavar="FILE",
        help="Generate audio file at specified path"
    )
    
    # Verbosity options
    verbosity_group = parser.add_argument_group("Verbosity")
    verbosity_group.add_argument(
        "--verbosity",
        choices=["verbose", "concise", "superbrief"],
        default="verbose",
        help="Speech verbosity level (default: verbose)"
    )
    
    # Input/output options
    io_group = parser.add_argument_group("Input/Output")
    io_group.add_argument(
        "-i", "--input",
        metavar="FILE",
        help="Read expressions from file (one per line)"
    )
    io_group.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Write output to file"
    )
    
    # Mode options
    mode_group = parser.add_argument_group("Mode")
    mode_group.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    mode_group.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (includes structure)"
    )
    mode_group.add_argument(
        "--structure",
        action="store_true",
        help="Show expression structure"
    )
    
    return parser


def process_expression(
    reader: MathReader,
    expression: str,
    args: argparse.Namespace,
    output: TextIO
) -> bool:
    """!
    @brief Process a single expression and write output.
    
    @param reader MathReader instance
    @param expression Expression to process
    @param args Parsed command-line arguments
    @param output Output stream
    @return True if successful, False if error occurred
    """
    try:
        if args.structure:
            # Output structure
            import json
            structure = reader.get_structure(expression)
            output.write(json.dumps(structure, indent=2))
            output.write("\n")
            
        elif args.json:
            # Full JSON output
            import json
            result = {
                "input": expression,
                "speech": reader.to_speech(expression),
                "braille": {
                    "nemeth": reader.to_braille(expression, "nemeth"),
                    "ueb": reader.to_braille(expression, "ueb"),
                },
                "structure": reader.get_structure(expression),
            }
            output.write(json.dumps(result, indent=2))
            output.write("\n")
            
        elif args.audio:
            # Generate audio
            audio_path = reader.to_audio(expression, args.audio)
            output.write(f"Audio saved to: {audio_path}\n")
            
        elif args.braille:
            # Output Braille
            braille = reader.to_braille(expression, args.notation)
            output.write(braille)
            output.write("\n")
            
        elif args.ssml:
            # Output SSML
            ssml = reader.to_ssml(expression)
            output.write(ssml)
            output.write("\n")
            
        else:
            # Default: speech text
            speech = reader.to_speech(expression)
            output.write(speech)
            output.write("\n")
        
        return True
        
    except ParseError as e:
        sys.stderr.write(f"Parse error: {e}\n")
        return False
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return False


def run_interactive(reader: MathReader, args: argparse.Namespace) -> None:
    """!
    @brief Run interactive mode.
    
    @param reader MathReader instance
    @param args Parsed arguments
    """
    print("Accessible Math Reader - Interactive Mode")
    print("Enter mathematical expressions (LaTeX or MathML)")
    print("Commands: :quit, :verbosity <level>, :braille, :speech")
    print("-" * 50)
    
    mode = "speech"
    
    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not line:
            continue
        
        # Handle commands
        if line.startswith(":"):
            cmd_parts = line[1:].split()
            cmd = cmd_parts[0].lower()
            
            if cmd in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            elif cmd == "verbosity" and len(cmd_parts) > 1:
                level = cmd_parts[1].lower()
                if level in ("verbose", "concise", "superbrief"):
                    reader.set_verbosity(level)
                    print(f"Verbosity set to: {level}")
                else:
                    print("Invalid verbosity level")
            elif cmd == "braille":
                mode = "braille"
                print("Switched to Braille output")
            elif cmd == "speech":
                mode = "speech"
                print("Switched to speech output")
            elif cmd == "help":
                print("Commands:")
                print("  :quit         - Exit interactive mode")
                print("  :verbosity X  - Set verbosity (verbose/concise/superbrief)")
                print("  :braille      - Switch to Braille output")
                print("  :speech       - Switch to speech output")
            else:
                print(f"Unknown command: {cmd}")
            continue
        
        # Process expression
        try:
            if mode == "braille":
                result = reader.to_braille(line, args.notation)
            else:
                result = reader.to_speech(line)
            print(result)
        except ParseError as e:
            print(f"Parse error: {e}")
        except Exception as e:
            print(f"Error: {e}")


def main(argv: Optional[list[str]] = None) -> int:
    """!
    @brief Main entry point for the CLI.
    
    @param argv Command-line arguments (uses sys.argv if None)
    @return Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Create configuration
    config = Config()
    config.speech.style = SpeechStyle(args.verbosity)
    
    # Create reader
    reader = MathReader(config)
    
    # Determine output stream
    output: TextIO
    if args.output:
        output = open(args.output, "w", encoding="utf-8")
    else:
        output = sys.stdout
    
    try:
        # Interactive mode
        if args.interactive:
            run_interactive(reader, args)
            return 0
        
        # Read from file
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                sys.stderr.write(f"Input file not found: {args.input}\n")
                return 1
            
            with open(input_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            success = True
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    if not process_expression(reader, line, args, output):
                        success = False
            
            return 0 if success else 1
        
        # Process single expression
        if args.expression:
            success = process_expression(reader, args.expression, args, output)
            return 0 if success else 1
        
        # No input provided
        parser.print_help()
        return 1
        
    finally:
        if args.output and output is not sys.stdout:
            output.close()


if __name__ == "__main__":
    sys.exit(main())
