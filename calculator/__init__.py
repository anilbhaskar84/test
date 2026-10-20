"""A small, safe calculator with an interactive CLI.

Public API::

    from calculator import Calculator

    calc = Calculator()
    print(calc.evaluate("2 + 2 * 3"))  # 8
"""

from .core import (
    Calculator,
    CalculatorError,
    DomainError,
    DivisionByZeroError,
    ParseError,
    format_result,
)

__all__ = [
    "Calculator",
    "CalculatorError",
    "DomainError",
    "DivisionByZeroError",
    "ParseError",
    "format_result",
    "__version__",
]

__version__ = "1.0.0"
