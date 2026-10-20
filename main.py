#!/usr/bin/env python3
"""Entry point for the calculator command line interface.

Usage
-----
    python main.py                # start the interactive REPL
    python main.py "2 + 2 * 3"    # evaluate a single expression
    python main.py --version
"""

import sys

from calculator.cli import main

if __name__ == "__main__":
    sys.exit(main())
