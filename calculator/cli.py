"""Command line interface for the calculator.

Run ``python main.py`` (no arguments) for the interactive REPL or
``python main.py "2 + 2 * 3"`` to evaluate a single expression.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .core import Calculator, CalculatorError, format_result

BANNER = """\
==================================================
  Python Calculator
  Type an expression, e.g.  2 + 2 * 3  or  sqrt(144)
  Commands: history | clear | help | exit
=================================================="""

HELP_TEXT = """\
Expression syntax
  + - * / // % **      arithmetic operators (** is power, right-associative)
  ( )                  grouping
  1e3, 2.5e-2          scientific notation
  pi, e, tau           constants
  Functions:
    sqrt, abs, floor, ceil, round, exp, log, log2, log10,
    sin, cos, tan, asin, acos, atan   (angles in radians)

REPL commands
  history    show previous evaluations
  clear      clear the evaluation history
  help       show this help
  exit/quit  leave the calculator

Examples
  2 + 2 * 3
  (1 + 2) * (3 + 4)
  sqrt(2) ** 2
  10 % 3
  sin(pi / 6)"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calculator",
        description="A small, safe arithmetic expression calculator "
        "(standard library only).",
    )
    parser.add_argument(
        "expression",
        nargs="?",
        help='expression to evaluate once, e.g. "2 + 2 * 3" '
        "(omit for interactive mode)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)
    calculator = Calculator()

    if args.expression is not None:
        try:
            result = calculator.evaluate(args.expression)
        except CalculatorError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(format_result(result))
        return 0

    print(BANNER)
    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        command = line.lower()
        if command in {"exit", "quit", "q"}:
            break
        if command in {"help", "?"}:
            print(HELP_TEXT)
            continue
        if command == "history":
            if calculator.history:
                for number, (expr, result) in enumerate(calculator.history, start=1):
                    print(f"{number}. {expr} = {format_result(result)}")
            else:
                print("History is empty.")
            continue
        if command == "clear":
            calculator.clear_history()
            print("History cleared.")
            continue
        try:
            result = calculator.evaluate(line)
        except CalculatorError as exc:
            print(f"Error: {exc}")
        else:
            print(format_result(result))
    print("Goodbye!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
