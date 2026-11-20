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
    "diff": lambda *a: sp.Derivative(*a), "Diff": lambda *a: sp.Derivative(*a),
    "integrate": lambda *a: sp.Integral(*a),
    "limit": lambda *a: sp.Limit(*a),
}

_KNOWN_SYMBOLS = {x, y, z, t, n, k}

# Operators whose evaluation is a "rule application" (derivative rules, integration, ...)
RULE_OPERATORS = ("Derivative", "Integral", "Limit", "diff(", "integrate(", "limit(", "binomial", "factorial", "!")


class ParseError(ValueError):
    pass


def _clean(text: str) -> str:
    text = text.strip().rstrip(".").replace("−", "-").replace("×", "*").replace("·", "*")
    text = text.replace("\\cdot", "*").replace("\\times", "*")
    text = re.sub(r"(\d)\s*!", r"factorial(\1)", text)
    return text


_LEIBNIZ = re.compile(r"^\s*d\s*/\s*d([a-z])\s*[\(\[](.*)[\)\]]\s*$")     # d/dx(...)  ->  Derivative(..., x)


def parse(text: str) -> sp.Expr:
    cleaned = _clean(text).replace("²", "**2").replace("³", "**3")
    cleaned = _LEIBNIZ.sub(r"Derivative(\2, \1)", cleaned)
    try:
        value = parse_expr(cleaned, local_dict=_LOCALS, transformations=_TRANSFORMS, evaluate=True)
    except Exception as exc:  # SymPy raises many exception types on bad input
        raise ParseError(f"could not parse {text!r}: {exc}") from exc
    if not isinstance(value, sp.Basic):
        raise ParseError(f"could not parse {text!r}: not a mathematical expression")
    unknown = value.free_symbols - _KNOWN_SYMBOLS
    if unknown:      # words or labels read as variables ("two plus twelve", "f(x)") are not math we can check
        raise ParseError(f"could not parse {text!r}: unknown name(s) {sorted(map(str, unknown))}")
    return value


def split_equals(text: str) -> list[str]:
    """'a = b = c' -> ['a', 'b', 'c'] (ignores '==', '<=', '>=')."""
    return [p for p in re.split(r"(?<![<>=!])=(?!=)", text) if p.strip()]


# A name that only labels the line: f(x), f'(x), f'(1), y, P, EV, F(3) ...
_LABEL = re.compile(r"^\s*([A-Za-z_]\w*)\s*('*)\s*(\([^=]*\))?\s*$")
_NOT_LABELS = {"x", "pi", "e", "E", "I", "oo", "inf"}


def _is_label(part: str) -> bool:
    m = _LABEL.match(part)
    if not m:
        return False
    name, primes, args = m.groups()
    if primes:
        return True                                   # f'(x), y'
    if name in _NOT_LABELS:
        return False
    return not (args and callable(_LOCALS.get(name)))   # sin(x), sqrt(2), binomial(8, 5) are math


def strip_prose(text: str) -> str:
    """'Substitute x = 1: 3*1 + 2' -> '3*1 + 2' (math syntax here never uses a colon)."""
    return text.rsplit(":", 1)[-1]


def step_parts(text: str) -> list[str]:
    """The mathematical expressions in one written step, without prose prefixes or labels.

    "f'(x) = 12*x**2 + 12*x - 5" -> ["12*x**2 + 12*x - 5"];  "56/256 = 7/32" -> ["56/256", "7/32"].
    """
    parts = split_equals(strip_prose(text))
    if len(parts) > 1:
        parts = [p for p in parts if not _is_label(p)] or parts
    return parts


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
    """Solutions of an equation step. Also reads 'x = 6 or x = -2' and 'x = 6, -2' as a union."""
    parts = _split_alternatives(eq_text)
    if len(parts) == 1:
        return _solve_one(eq_text, var)
    sols: set = set()
    for part in parts:
        sols |= _solve_one(part, var) if "=" in part else {sp.nsimplify(parse(part))}
    return sols


def _solve_one(eq_text: str, var: sp.Symbol) -> set:
    lhs, rhs = (parse(p) for p in _two_sides(eq_text))
    sols = sp.solve(sp.Eq(lhs, rhs), var)
    return {sp.nsimplify(sp.simplify(s)) for s in sols}


def _split_alternatives(text: str) -> list[str]:
    """Split on ' or ', ',' and ';' that are outside parentheses."""
    text = re.sub(r"\s+or\s+", ",", text.replace(";", ","))
    parts, depth, cur = [], 0, ""
    for ch in text:
        depth += ch in "([{"
        depth -= ch in ")]}"
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p for p in parts if p.strip()]


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
