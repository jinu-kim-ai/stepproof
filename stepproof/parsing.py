"""Safe parsing of model-written math into SymPy objects, and equivalence checks."""
from __future__ import annotations

import random
import re

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

x, y, z, t, n, k = sp.symbols("x y z t n k")
_TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)

# Only these names are visible to the parser - no arbitrary Python execution.
_LOCALS = {
    "x": x, "y": y, "z": z, "t": t, "n": n, "k": k,
    "pi": sp.pi, "e": sp.E, "E": sp.E, "I": sp.I, "oo": sp.oo, "inf": sp.oo,
    "sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "ln": sp.log,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "Abs": sp.Abs, "abs": sp.Abs,
    "Rational": sp.Rational, "binomial": sp.binomial, "factorial": sp.factorial,
    "Derivative": sp.Derivative, "Integral": sp.Integral, "Limit": sp.Limit, "Subs": sp.Subs,
    "diff": lambda *a: sp.Derivative(*a), "integrate": lambda *a: sp.Integral(*a),
    "limit": lambda *a: sp.Limit(*a),
}

# Operators whose evaluation is a "rule application" (derivative rules, integration, ...)
RULE_OPERATORS = ("Derivative", "Integral", "Limit", "diff(", "integrate(", "limit(", "binomial", "factorial", "!")


class ParseError(ValueError):
    pass


def _clean(text: str) -> str:
    text = text.strip().rstrip(".").replace("−", "-").replace("×", "*").replace("·", "*")
    text = text.replace("\\cdot", "*").replace("\\times", "*")
    text = re.sub(r"(\d)\s*!", r"factorial(\1)", text)
    return text


def parse(text: str) -> sp.Expr:
    try:
        return parse_expr(_clean(text), local_dict=_LOCALS, transformations=_TRANSFORMS, evaluate=True)
    except Exception as exc:  # SymPy raises many exception types on bad input
        raise ParseError(f"could not parse {text!r}: {exc}") from exc


def split_equals(text: str) -> list[str]:
    """'a = b = c' -> ['a', 'b', 'c'] (ignores '==', '<=', '>=')."""
    return [p for p in re.split(r"(?<![<>=!])=(?!=)", text) if p.strip()]


def parse_answer_set(text: str) -> list[sp.Expr]:
    """Parse a final answer such as 'x = 2, x = -3', '{2, -3}' or '2 or -3'."""
    text = re.sub(r"\b[a-z]\s*=", "", text.strip().strip("{}[]()").replace(" or ", ","))
    return [parse(p) for p in text.split(",") if p.strip()]


def has_rule_operator(text: str) -> bool:
    return any(op in text for op in RULE_OPERATORS)


def equivalent(a: sp.Expr, b: sp.Expr, samples: int = 6) -> bool:
    """True if a and b are mathematically equal (symbolic check, numeric fallback)."""
    try:
        diff = sp.simplify(sp.sympify(a).doit() - sp.sympify(b).doit())
        if diff == 0:
            return True
        free = sorted(diff.free_symbols, key=str)
        if not free:
            val = complex(sp.N(diff))
            return abs(val) < 1e-9
        rng = random.Random(0)
        for _ in range(samples):
            point = {s: sp.Rational(rng.randint(-40, 40), rng.randint(1, 9)) + sp.Rational(1, 7) for s in free}
            val = complex(sp.N(diff.subs(point)))
            if abs(val) > 1e-7:
                return False
        return True
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def solution_set(eq_text: str, var: sp.Symbol = x) -> set:
    lhs, rhs = (parse(p) for p in _two_sides(eq_text))
    sols = sp.solve(sp.Eq(lhs, rhs), var)
    return {sp.nsimplify(sp.simplify(s)) for s in sols}


def equation_poly(eq_text: str, var: sp.Symbol = x) -> sp.Poly | None:
    lhs, rhs = (parse(p) for p in _two_sides(eq_text))
    try:
        return sp.Poly(sp.expand(lhs - rhs), var)
    except sp.PolynomialError:
        return None


def _two_sides(eq_text: str) -> tuple[str, str]:
    parts = split_equals(eq_text)
    if len(parts) != 2:
        raise ParseError(f"expected one '=' in equation step {eq_text!r}")
    return parts[0], parts[1]


def same_set(a, b) -> bool:
    a, b = list(a), list(b)
    return len(a) == len(b) and all(any(equivalent(p, q) for q in b) for p in a) and \
        all(any(equivalent(q, p) for p in a) for q in b)
