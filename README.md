# Python Calculator

A small but complete calculator project written in **pure Python**
(standard library only — no third-party dependencies). It evaluates
arithmetic expressions safely using a hand-written tokenizer and
recursive-descent parser; `eval` is never used, so an expression can only
contain numbers, operators, math functions and constants.

## Features

- Safe expression evaluator (no `eval`, no code execution)
- Arithmetic: `+  -  *  /  //  %  **` (power is right-associative)
- Parentheses and unary minus/plus
- Scientific notation (`1e3`, `2.5e-2`)
- Math functions: `sqrt, abs, floor, ceil, round, exp, log, log2, log10,`
  `sin, cos, tan, asin, acos, atan`
- Constants: `pi`, `e`, `tau`
- Evaluation history with `history` / `clear` commands
- Interactive REPL and one-shot CLI mode
- Descriptive, typed error hierarchy
  (`ParseError`, `DivisionByZeroError`, `DomainError`)
- Unit test suite (standard-library `unittest`)

## Project structure

```
.
├── main.py                  # CLI entry point
├── calculator/
│   ├── __init__.py          # public API
│   ├── core.py              # tokenizer, parser, Calculator
│   └── cli.py               # argparse CLI + interactive REPL
├── tests/
│   ├── __init__.py
│   └── test_calculator.py   # unit tests
├── README.md
├── requirements.txt
└── .gitignore
```

## Requirements

Python 3.8+ — no external packages needed.

## Usage

### One-shot mode

```bash
python3 main.py "2 + 2 * 3"
# 8

python3 main.py "sqrt(2) ** 2"
# 2
```

### Interactive mode

```bash
python3 main.py
```

```
==================================================
  Python Calculator
  Type an expression, e.g.  2 + 2 * 3  or  sqrt(144)
  Commands: history | clear | help | exit
==================================================
>>> 2 + 2 * 3
8
>>> sqrt(144)
12
>>> 1 / 0
Error: Cannot divide by zero
>>> history
1. 2 + 2 * 3 = 8
2. sqrt(144) = 12
>>> exit
Goodbye!
```

REPL commands: `history`, `clear`, `help` / `?`, `exit` / `quit` / `q`.

### As a library

```python
from calculator import Calculator

calc = Calculator()
print(calc.evaluate("(1 + 2) * (3 + 4)"))   # 21
print(calc.add(2, 3))                        # 5
print(Calculator.divide(10, 4))              # 2.5
print(calc.history)                          # [('(1 + 2) * (3 + 4)', 21.0)]
```

### Errors

All errors inherit from `calculator.CalculatorError`:

| Exception               | Raised when                                          |
| ----------------------- | ---------------------------------------------------- |
| `ParseError`            | the expression is syntactically invalid              |
| `DivisionByZeroError`   | division, floor division or modulo by zero           |
| `DomainError`           | e.g. `sqrt(-1)`, `log(0)` or a non-finite result     |

## Running the tests

```bash
python3 -m unittest discover -s tests -v
```

## Notes

- `log` is the natural logarithm; `log2` and `log10` are also available.
- Trig functions take radians.
- `**` follows the usual math convention: `-2 ** 2` is `-(2 ** 2) == -4`;
  use `(-2) ** 2` for `4`.
