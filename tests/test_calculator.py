"""Unit tests for the calculator package."""

import math
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from calculator import (  # noqa: E402
    Calculator,
    CalculatorError,
    DomainError,
    DivisionByZeroError,
    ParseError,
    format_result,
)


class TestBasicOperations(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_addition(self):
        self.assertEqual(self.calc.evaluate("2 + 3"), 5)

    def test_subtraction(self):
        self.assertEqual(self.calc.evaluate("5 - 2"), 3)

    def test_multiplication(self):
        self.assertEqual(self.calc.evaluate("4 * 3"), 12)

    def test_division(self):
        self.assertEqual(self.calc.evaluate("10 / 4"), 2.5)

    def test_floor_division(self):
        self.assertEqual(self.calc.evaluate("7 // 2"), 3)

    def test_modulo(self):
        self.assertEqual(self.calc.evaluate("10 % 3"), 1)

    def test_power(self):
        self.assertEqual(self.calc.evaluate("2 ** 10"), 1024)

    def test_precedence(self):
        self.assertEqual(self.calc.evaluate("2 + 2 * 3"), 8)

    def test_parentheses(self):
        self.assertEqual(self.calc.evaluate("(2 + 2) * 3"), 12)

    def test_nested_parentheses(self):
        self.assertEqual(self.calc.evaluate("((1 + 2) * (3 + 4)) / 7"), 3)

    def test_unary_minus(self):
        self.assertEqual(self.calc.evaluate("-2 + 5"), 3)
        self.assertEqual(self.calc.evaluate("3 * -2"), -6)

    def test_unary_plus(self):
        self.assertEqual(self.calc.evaluate("+2 * 3"), 6)

    def test_power_is_right_associative(self):
        self.assertEqual(self.calc.evaluate("2 ** 3 ** 2"), 512)

    def test_power_with_unary_minus_base(self):
        # Standard math precedence: -2 ** 2 == -(2 ** 2) == -4
        self.assertEqual(self.calc.evaluate("-2 ** 2"), -4)
        self.assertEqual(self.calc.evaluate("(-2) ** 2"), 4)

    def test_float_result(self):
        self.assertAlmostEqual(self.calc.evaluate("0.1 + 0.2"), 0.3)

    def test_scientific_notation(self):
        self.assertEqual(self.calc.evaluate("1e3 + 1"), 1001)
        self.assertAlmostEqual(self.calc.evaluate("2.5e-2"), 0.025)

    def test_whitespace_is_ignored(self):
        self.assertEqual(self.calc.evaluate("  2+\t2\n"), 4)

    def test_chained_operations(self):
        self.assertEqual(self.calc.evaluate("1 + 2 - 3 + 4"), 4)


class TestFunctionsAndConstants(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_sqrt(self):
        self.assertEqual(self.calc.evaluate("sqrt(16)"), 4)

    def test_abs(self):
        self.assertEqual(self.calc.evaluate("abs(-5)"), 5)

    def test_trig(self):
        self.assertAlmostEqual(self.calc.evaluate("sin(0)"), 0.0)
        self.assertAlmostEqual(self.calc.evaluate("cos(0)"), 1.0)
        self.assertAlmostEqual(self.calc.evaluate("sin(pi / 2)"), 1.0)

    def test_log_functions(self):
        self.assertAlmostEqual(self.calc.evaluate("log(e)"), 1.0)
        self.assertAlmostEqual(self.calc.evaluate("log2(8)"), 3.0)
        self.assertAlmostEqual(self.calc.evaluate("log10(1000)"), 3.0)

    def test_rounding_functions(self):
        self.assertEqual(self.calc.evaluate("floor(3.7)"), 3)
        self.assertEqual(self.calc.evaluate("ceil(3.2)"), 4)
        self.assertEqual(self.calc.evaluate("round(2.5)"), 2)

    def test_nested_function_calls(self):
        self.assertEqual(self.calc.evaluate("sqrt(abs(-16))"), 4)
        self.assertEqual(self.calc.evaluate("abs(sqrt(4) - 3)"), 1)

    def test_constants(self):
        self.assertAlmostEqual(self.calc.evaluate("pi"), math.pi)
        self.assertAlmostEqual(self.calc.evaluate("e"), math.e)
        self.assertAlmostEqual(self.calc.evaluate("2 * pi"), 2 * math.pi)
        self.assertAlmostEqual(self.calc.evaluate("tau"), 2 * math.pi)


class TestErrors(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_division_by_zero(self):
        with self.assertRaises(DivisionByZeroError):
            self.calc.evaluate("1 / 0")

    def test_floor_division_by_zero(self):
        with self.assertRaises(DivisionByZeroError):
            self.calc.evaluate("5 // 0")

    def test_modulo_by_zero(self):
        with self.assertRaises(DivisionByZeroError):
            self.calc.evaluate("5 % 0")

    def test_zero_negative_power(self):
        with self.assertRaises(DivisionByZeroError):
            self.calc.evaluate("0 ** -1")

    def test_sqrt_negative(self):
        with self.assertRaises(DomainError):
            self.calc.evaluate("sqrt(-1)")

    def test_log_of_zero(self):
        with self.assertRaises(DomainError):
            self.calc.evaluate("log(0)")

    def test_non_finite_result(self):
        with self.assertRaises(DomainError):
            self.calc.evaluate("1e308 * 10")

    def test_empty_expression(self):
        with self.assertRaises(ParseError):
            self.calc.evaluate("")
        with self.assertRaises(ParseError):
            self.calc.evaluate("   ")

    def test_incomplete_expression(self):
        with self.assertRaises(ParseError):
            self.calc.evaluate("2 +")
        with self.assertRaises(ParseError):
            self.calc.evaluate("(2 + 3")

    def test_trailing_tokens(self):
        with self.assertRaises(ParseError):
            self.calc.evaluate("2 3")
        with self.assertRaises(ParseError):
            self.calc.evaluate("2 )")

    def test_unknown_identifier(self):
        with self.assertRaises(ParseError):
            self.calc.evaluate("x + 1")

    def test_unknown_function(self):
        with self.assertRaises(ParseError):
            self.calc.evaluate("foo(1)")

    def test_invalid_character(self):
        with self.assertRaises(ParseError):
            self.calc.evaluate("2 & 3")

    def test_invalid_number(self):
        with self.assertRaises(ParseError):
            self.calc.evaluate("1.2.3")

    def test_errors_do_not_pollute_history(self):
        with self.assertRaises(CalculatorError):
            self.calc.evaluate("1 / 0")
        self.assertEqual(self.calc.history, [])

    def test_all_errors_are_calculator_errors(self):
        for error in (ParseError, DivisionByZeroError, DomainError):
            self.assertTrue(issubclass(error, CalculatorError))


class TestBasicBuildingBlocks(unittest.TestCase):
    def test_add(self):
        self.assertEqual(Calculator.add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(Calculator.subtract(5, 2), 3)

    def test_multiply(self):
        self.assertEqual(Calculator.multiply(4, 2.5), 10)

    def test_divide(self):
        self.assertEqual(Calculator.divide(10, 4), 2.5)

    def test_divide_by_zero(self):
        with self.assertRaises(DivisionByZeroError):
            Calculator.divide(1, 0)

    def test_power(self):
        self.assertEqual(Calculator.power(2, 8), 256)

    def test_modulo(self):
        self.assertEqual(Calculator.modulo(10, 3), 1)

    def test_sqrt(self):
        self.assertEqual(Calculator.sqrt(9), 3)
        with self.assertRaises(DomainError):
            Calculator.sqrt(-4)


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_history_records_evaluations(self):
        self.calc.evaluate("1 + 1")
        self.calc.evaluate("2 * 3")
        self.assertEqual(self.calc.history, [("1 + 1", 2), ("2 * 3", 6)])

    def test_history_returns_a_copy(self):
        self.calc.evaluate("1 + 1")
        history = self.calc.history
        history.clear()
        self.assertEqual(len(self.calc.history), 1)

    def test_clear_history(self):
        self.calc.evaluate("1 + 1")
        self.calc.clear_history()
        self.assertEqual(self.calc.history, [])


class TestFormatResult(unittest.TestCase):
    def test_integer_value(self):
        self.assertEqual(format_result(4.0), "4")

    def test_float_value(self):
        self.assertEqual(format_result(0.5), "0.5")

    def test_large_value(self):
        self.assertEqual(format_result(1e20), "1e+20")


class TestCli(unittest.TestCase):
    def _run_cli(self, stdin: str = "", *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py"), *args],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(PROJECT_ROOT),
        )

    def test_single_expression(self):
        completed = self._run_cli("", "2 + 2 * 3")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "8")

    def test_single_expression_error(self):
        completed = self._run_cli("", "1 / 0")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("Error:", completed.stderr)

    def test_version_flag(self):
        completed = self._run_cli("", "--version")
        self.assertEqual(completed.returncode, 0)
        self.assertIn("calculator", completed.stdout)

    def test_repl_scripted_session(self):
        stdin = "1 + 1\nsqrt(144)\n1 / 0\nhistory\nexit\n"
        completed = self._run_cli(stdin)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("2", completed.stdout)
        self.assertIn("12", completed.stdout)
        self.assertIn("Error: Cannot divide by zero", completed.stdout)
        self.assertIn("1. 1 + 1 = 2", completed.stdout)
        self.assertIn("2. sqrt(144) = 12", completed.stdout)
        self.assertNotIn("1 / 0 = ", completed.stdout)


if __name__ == "__main__":
    unittest.main()
