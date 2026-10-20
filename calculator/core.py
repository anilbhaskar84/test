"""Core calculation engine for the calculator project.

This module implements a small, *safe* arithmetic expression evaluator
using a hand-written tokenizer and recursive-descent parser.  ``eval``
is never used, so an expression can only contain numbers, operators,
the supported math functions and the supported constants.

Grammar::

    expr    := term (('+' | '-') term)*
    term    := unary (('*' | '/' | '//' | '%') unary)*
    unary   := ('-' | '+') unary | power
    power   := primary ('**' unary)?        # right-associative power
    primary := NUMBER
              | IDENT '(' expr ')'          # function call
              | IDENT                       # constant
              | '(' expr ')'
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto

__all__ = [
    "Calculator",
    "CalculatorError",
    "DomainError",
    "DivisionByZeroError",
    "ParseError",
    "format_result",
]


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #
class CalculatorError(Exception):
    """Base class for every error raised by the calculator."""


class ParseError(CalculatorError):
    """Raised when an expression cannot be tokenized or parsed."""


class DivisionByZeroError(CalculatorError):
    """Raised for division, floor division or modulo by zero."""


class DomainError(CalculatorError):
    """Raised when a function is used outside its domain (e.g. ``sqrt(-1)``)."""


# --------------------------------------------------------------------------- #
# Supported math functions and constants
# --------------------------------------------------------------------------- #
_FUNCTIONS = {
    "abs": abs,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "exp": math.exp,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,
}

_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}


# --------------------------------------------------------------------------- #
# Tokenizer
# --------------------------------------------------------------------------- #
class TokenType(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    DSTAR = auto()
    DSLASH = auto()
    PERCENT = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    IDENT = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int


class _Tokenizer:
    """Converts an expression string into a list of tokens."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def tokenize(self):
        tokens = []
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isspace():
                self.pos += 1
            elif char.isdigit() or char == ".":
                self._read_number(tokens)
            elif char.isalpha() or char == "_":
                self._read_identifier(tokens)
            else:
                self._read_operator(tokens)
        tokens.append(Token(TokenType.EOF, "", len(self.text)))
        return tokens

    def _read_number(self, tokens):
        start = self.pos
        text = self.text
        length = len(text)
        while self.pos < length and (text[self.pos].isdigit() or text[self.pos] == "."):
            self.pos += 1
        # Optional exponent part, e.g. ``1.5e10`` or ``2E-3``.
        if self.pos < length and text[self.pos] in "eE":
            probe = self.pos + 1
            if probe < length and text[probe] in "+-":
                probe += 1
            if probe < length and text[probe].isdigit():
                self.pos = probe
                while self.pos < length and text[self.pos].isdigit():
                    self.pos += 1
        literal = text[start:self.pos]
        try:
            value = float(literal)
        except ValueError:
            raise ParseError(f"Invalid number {literal!r} at position {start}") from None
        tokens.append(Token(TokenType.NUMBER, repr(value), start))

    def _read_identifier(self, tokens):
        start = self.pos
        while self.pos < len(self.text) and (
            self.text[self.pos].isalnum() or self.text[self.pos] == "_"
        ):
            self.pos += 1
        tokens.append(Token(TokenType.IDENT, self.text[start:self.pos], start))

    def _read_operator(self, tokens):
        start = self.pos
        two_char = self.text[self.pos : self.pos + 2]
        if two_char == "**":
            token_type = TokenType.DSTAR
            self.pos += 2
        elif two_char == "//":
            token_type = TokenType.DSLASH
            self.pos += 2
        else:
            single = self.text[self.pos]
            token_type = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "%": TokenType.PERCENT,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                ",": TokenType.COMMA,
            }.get(single)
            if token_type is None:
                raise ParseError(f"Unexpected character {single!r} at position {start}")
            self.pos += 1
        tokens.append(Token(token_type, self.text[start:self.pos], start))


# --------------------------------------------------------------------------- #
# Parser / evaluator
# --------------------------------------------------------------------------- #
class _Parser:
    """Recursive-descent parser that evaluates the token stream directly."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    # -- helpers ----------------------------------------------------------- #
    def _current(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> Token:
        token = self._current()
        if token.type is not TokenType.EOF:
            self.index += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        token = self._current()
        if token.type is not token_type:
            found = (
                "end of expression" if token.type is TokenType.EOF else repr(token.value)
            )
            raise ParseError(
                f"Expected {token_type.name.lower()} but found {found} "
                f"at position {token.position}"
            )
        return self._advance()

    # -- grammar rules ----------------------------------------------------- #
    def parse(self) -> float:
        value = self._expr()
        token = self._current()
        if token.type is not TokenType.EOF:
            raise ParseError(
                f"Unexpected token {token.value!r} at position {token.position}"
            )
        return value

    def _expr(self) -> float:
        value = self._term()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            operator = self._advance()
            right = self._term()
            value = value + right if operator.type is TokenType.PLUS else value - right
        return value

    def _term(self) -> float:
        value = self._unary()
        while self._current().type in (
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.DSLASH,
            TokenType.PERCENT,
        ):
            operator = self._advance()
            right = self._unary()
            if operator.type is TokenType.STAR:
                value *= right
            elif operator.type is TokenType.SLASH:
                if right == 0:
                    raise DivisionByZeroError("Cannot divide by zero")
                value /= right
            elif operator.type is TokenType.DSLASH:
                if right == 0:
                    raise DivisionByZeroError("Cannot perform floor division by zero")
                value = math.floor(value / right)
            else:  # PERCENT
                if right == 0:
                    raise DivisionByZeroError("Cannot perform modulo by zero")
                value %= right
        return value

    def _unary(self) -> float:
        token = self._current()
        if token.type is TokenType.MINUS:
            self._advance()
            return -self._unary()
        if token.type is TokenType.PLUS:
            self._advance()
            return self._unary()
        return self._power()

    def _power(self) -> float:
        base = self._primary()
        if self._current().type is not TokenType.DSTAR:
            return base
        self._advance()
        exponent = self._unary()  # right-associative: 2 ** 3 ** 2 == 2 ** 9
        if base == 0 and exponent < 0:
            raise DivisionByZeroError("Cannot raise zero to a negative power")
        try:
            return base ** exponent
        except ZeroDivisionError as exc:
            raise DivisionByZeroError("Cannot raise zero to a negative power") from exc
        except OverflowError as exc:
            raise DomainError("Overflow in exponentiation") from exc
        except ValueError as exc:
            raise DomainError(f"Invalid power: {base} ** {exponent}") from exc

    def _primary(self) -> float:
        token = self._current()
        if token.type is TokenType.NUMBER:
            self._advance()
            return float(token.value)
        if token.type is TokenType.LPAREN:
            self._advance()
            value = self._expr()
            self._expect(TokenType.RPAREN)
            return value
        if token.type is TokenType.IDENT:
            self._advance()
            if self._current().type is TokenType.LPAREN:
                return self._call_function(token.value, token.position)
            if token.value in _CONSTANTS:
                return _CONSTANTS[token.value]
            raise ParseError(
                f"Unknown identifier {token.value!r} at position {token.position}"
            )
        if token.type is TokenType.EOF:
            raise ParseError("Unexpected end of expression")
        raise ParseError(f"Unexpected token {token.value!r} at position {token.position}")

    def _call_function(self, name: str, position: int) -> float:
        function = _FUNCTIONS.get(name)
        if function is None:
            raise ParseError(f"Unknown function {name!r} at position {position}")
        self._expect(TokenType.LPAREN)
        argument = self._expr()
        self._expect(TokenType.RPAREN)
        try:
            return function(argument)
        except ZeroDivisionError as exc:
            raise DivisionByZeroError(f"{name}(0) is undefined") from exc
        except ValueError as exc:
            raise DomainError(f"{name}({argument}) is not defined for this input") from exc


# --------------------------------------------------------------------------- #
# Public calculator
# --------------------------------------------------------------------------- #
def format_result(value) -> str:
    """Return a compact, human-friendly representation of *value*."""
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        if value.is_integer() and abs(value) < 1e16:
            return str(int(value))
    return repr(value)


class Calculator:
    """Stateful calculator that remembers the history of its evaluations."""

    def __init__(self) -> None:
        self._history = []  # type: list[tuple[str, float]]

    # -- basic building blocks --------------------------------------------- #
    @staticmethod
    def add(a: float, b: float) -> float:
        """Return ``a + b``."""
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Return ``a - b``."""
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Return ``a * b``."""
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        """Return ``a / b`` or raise :class:`DivisionByZeroError`."""
        if b == 0:
            raise DivisionByZeroError("Cannot divide by zero")
        return a / b

    @staticmethod
    def power(a: float, b: float) -> float:
        """Return ``a ** b``."""
        if a == 0 and b < 0:
            raise DivisionByZeroError("Cannot raise zero to a negative power")
        try:
            return a ** b
        except OverflowError as exc:
            raise DomainError("Overflow in exponentiation") from exc
        except ValueError as exc:
            raise DomainError(f"Invalid power: {a} ** {b}") from exc

    @staticmethod
    def modulo(a: float, b: float) -> float:
        """Return ``a % b`` or raise :class:`DivisionByZeroError`."""
        if b == 0:
            raise DivisionByZeroError("Cannot perform modulo by zero")
        return a % b

    @staticmethod
    def sqrt(a: float) -> float:
        """Return the square root of *a* or raise :class:`DomainError`."""
        if a < 0:
            raise DomainError(f"sqrt({a}) is not defined for negative numbers")
        return math.sqrt(a)

    # -- expression evaluation ---------------------------------------------- #
    def evaluate(self, expression: str):
        """Safely evaluate an arithmetic expression and record it in history."""
        if not isinstance(expression, str) or not expression.strip():
            raise ParseError("Expression must be a non-empty string")
        tokens = _Tokenizer(expression).tokenize()
        result = _Parser(tokens).parse()
        if math.isnan(result) or math.isinf(result):
            raise DomainError(
                f"Expression does not have a finite result: {expression!r}"
            )
        self._history.append((expression, result))
        return result

    # -- history ------------------------------------------------------------- #
    @property
    def history(self):
        """A copy of the ``(expression, result)`` pairs evaluated so far."""
        return list(self._history)

    def clear_history(self) -> None:
        """Forget every previous evaluation."""
        self._history.clear()
