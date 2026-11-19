"""Deterministic generator for competition-style problems with SymPy-checked answers.

13 templates across algebra, calculus and probability. Each problem carries a
reference step-by-step solution (used by the simulated models and as a worked
example) and, where it applies, a realistic *misapplied-rule* variant of one step.
With the default 40 problems per template the benchmark has 520 problems.
"""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

import sympy as sp

x = sp.Symbol("x")
R = sp.Rational


@dataclass
class Problem:
    id: str
    domain: str              # algebra | calculus | probability
    topic: str
    kind: str                # evaluate | solve
    statement: str           # natural-language prompt shown to the model
    expression: str          # SymPy-parsable expression (evaluate) or equation (solve)
    answer: str
    reference_steps: list[str]
    variable: str = "x"
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def s(e) -> str:
    return sp.sstr(e)


def nz(rng: random.Random, lo: int, hi: int) -> int:
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


# ------------------------------------------------------------------ algebra
def linear_one_side(rng, i):
    a, x0, b = rng.randint(2, 12), rng.randint(-15, 15), nz(rng, -20, 20)
    c = a * x0 + b
    eq = f"{s(a*x + b)} = {c}"
    return Problem(f"alg-lin1-{i:03d}", "algebra", "linear equation", "solve",
                   f"Solve for x: {eq}", eq, str(x0), [f"{a}*x = {c - b}", f"x = {x0}"])


def linear_two_sides(rng, i):
    a, c = rng.randint(2, 12), rng.randint(-9, 9)
    while c == a:
        c = rng.randint(-9, 9)
    x0, b = rng.randint(-12, 12), rng.randint(-20, 20)
    d = (a - c) * x0 + b
    eq = f"{s(a*x + b)} = {s(c*x + d)}"
    return Problem(f"alg-lin2-{i:03d}", "algebra", "linear equation (both sides)", "solve",
                   f"Solve for x: {eq}", eq, str(x0), [f"{a - c}*x = {d - b}", f"x = {x0}"])


def quadratic(rng, i):
    r1, r2 = rng.randint(-9, 9), rng.randint(-9, 9)
    while r2 == r1:
        r2 = rng.randint(-9, 9)
    p, q = -(r1 + r2), r1 * r2
    eq = f"{s(x**2 + p*x + q)} = 0"
    steps = [f"{s(x**2 + p*x)} = {-q}", f"{s(sp.Mul(x - r1, x - r2, evaluate=False))} = 0"]
    return Problem(f"alg-quad-{i:03d}", "algebra", "quadratic equation", "solve",
                   f"Solve for x (give all real solutions): {eq}", eq, f"{r1}, {r2}", steps)


def fractions(rng, i):
    a, b, c, d = rng.randint(1, 9), rng.randint(2, 9), rng.randint(1, 9), rng.randint(2, 9)
    e = rng.randint(2, 12)
    expr = f"({a}/{b} + {c}/{d})*{e}"
    val = (R(a, b) + R(c, d)) * e
    steps = [f"({a*d + c*b}/{b*d})*{e}", f"{(a*d + c*b)*e}/{b*d}", s(val)]
    return Problem(f"alg-frac-{i:03d}", "algebra", "fraction arithmetic", "evaluate",
                   f"Compute exactly: {expr}", expr, s(val), steps)


def expand_difference(rng, i):
    a, b = nz(rng, -9, 9), nz(rng, -9, 9)
    expr = f"(x + {a})**2 - (x - {b})**2".replace("+ -", "- ").replace("- -", "+ ")
    ans = sp.expand((x + a)**2 - (x - b)**2)
    steps = [f"({s(sp.expand((x + a)**2))}) - ({s(sp.expand((x - b)**2))})", s(ans)]
    return Problem(f"alg-expand-{i:03d}", "algebra", "polynomial simplification", "evaluate",
                   f"Expand and simplify: {expr}", expr, s(ans), steps)


# ------------------------------------------------------------------ calculus
def derivative_product(rng, i):
    m = rng.randint(2, 6)
    v = rng.choice([sp.sin(x), sp.cos(x), sp.exp(x), sp.log(x)])
    u = x**m
    f = u * v
    ans = sp.expand(sp.diff(f, x))
    steps = [f"Derivative({s(u)}, x)*{s(v)} + {s(u)}*Derivative({s(v)}, x)",
             f"{s(sp.diff(u, x))}*{s(v)} + {s(u)}*{s(sp.diff(v, x))}"]
    wrong = f"{s(sp.diff(u, x))}*{s(sp.diff(v, x))}"  # product of derivatives
    return Problem(f"calc-prod-{i:03d}", "calculus", "product rule", "evaluate",
                   f"Differentiate with respect to x: f(x) = {s(f)}", f"Derivative({s(f)}, x)", s(ans), steps,
                   meta={"misapplied": {"index": 1, "text": wrong, "rule": "product of derivatives instead of product rule"}})


def derivative_at_point(rng, i):
    a, b, c, p = nz(rng, -5, 5), rng.randint(-6, 6), rng.randint(-9, 9), nz(rng, -3, 4)
    f = a*x**3 + b*x**2 + c*x
    val = sp.diff(f, x).subs(x, p)
    steps = [f"{3*a}*({p})**2 + {2*b}*({p}) + {c}", f"{3*a*p*p} + {2*b*p} + {c}", s(val)]
    wrong = f"{3*a}*({p})**3 + {2*b}*({p})**2 + {c}*({p})"  # forgot to lower the exponent
    return Problem(f"calc-dpt-{i:03d}", "calculus", "derivative at a point", "evaluate",
                   f"Let f(x) = {s(f)}. Compute f'({p}).", f"Subs(Derivative({s(f)}, x), x, {p})", s(val), steps,
                   meta={"misapplied": {"index": 0, "text": wrong, "rule": "power rule without reducing the exponent"}})


def definite_integral(rng, i):
    a, b, c = nz(rng, -6, 6), rng.randint(-6, 6), rng.randint(-6, 6)
    lo = rng.randint(-2, 1)
    hi = lo + rng.randint(1, 3)
    f = a*x**2 + b*x + c
    val = sp.integrate(f, (x, lo, hi))

    def F(v, divide=True):
        if divide:
            return f"{a}*({v})**3/3 + {b}*({v})**2/2 + {c}*({v})"
        return f"{a}*({v})**3 + {b}*({v})**2 + {c}*({v})"

    Fh = R(a, 3) * hi**3 + R(b, 2) * hi**2 + c * hi
    Fl = R(a, 3) * lo**3 + R(b, 2) * lo**2 + c * lo
    steps = [f"({F(hi)}) - ({F(lo)})", f"({s(Fh)}) - ({s(Fl)})", s(val)]
    wrong = f"({F(hi, False)}) - ({F(lo, False)})"  # forgot to divide by n+1
    return Problem(f"calc-int-{i:03d}", "calculus", "definite integral", "evaluate",
                   f"Evaluate the integral of {s(f)} from x = {lo} to x = {hi}.",
                   f"Integral({s(f)}, (x, {lo}, {hi}))", s(val), steps,
                   meta={"misapplied": {"index": 0, "text": wrong, "rule": "antiderivative without dividing by n+1"}})


def removable_limit(rng, i):
    a = nz(rng, -9, 9)
    expr = f"Limit(({s(x**2 - a*a)})/({s(x - a)}), x, {a})"
    steps = [f"Limit({s(x + a)}, x, {a})", f"({a}) + ({a})", str(2 * a)]
    wrong = "0"  # plugged in and treated 0/0 as 0
    return Problem(f"calc-lim-{i:03d}", "calculus", "limit (removable discontinuity)", "evaluate",
                   f"Evaluate the limit as x -> {a} of ({s(x**2 - a*a)})/({s(x - a)}).", expr, str(2 * a), steps,
                   meta={"misapplied": {"index": 1, "text": wrong, "rule": "treated 0/0 as 0 instead of factoring"}})


# ------------------------------------------------------------------ probability
def binomial_prob(rng, i):
    n = rng.randint(3, 8)
    k = rng.randint(1, n - 1)
    p = rng.choice([R(1, 2), R(1, 3), R(1, 4), R(1, 6)])
    C = sp.binomial(n, k)
    val = C * p**k * (1 - p)**(n - k)
    expr = f"binomial({n}, {k})*({p})**{k}*({1 - p})**{n - k}"
    steps = [f"{C}*({p**k})*({(1 - p)**(n - k)})", s(val)]
    perm = sp.factorial(n) / sp.factorial(n - k)
    wrong = f"{perm}*({p**k})*({(1 - p)**(n - k)})"  # used permutations instead of combinations
    return Problem(f"prob-binom-{i:03d}", "probability", "binomial probability", "evaluate",
                   f"An event has probability {p} on each of {n} independent trials. "
                   f"What is the probability it happens exactly {k} times?", expr, s(val), steps,
                   meta={"misapplied": {"index": 0, "text": wrong, "rule": "nPk instead of nCk"}})


def without_replacement(rng, i):
    r = rng.randint(2, 9)
    tot = r + rng.randint(2, 12)
    val = R(r, tot) * R(r - 1, tot - 1)
    expr = f"({r}/{tot})*({r - 1}/{tot - 1})"
    steps = [f"{r*(r-1)}/{tot*(tot-1)}", s(val)]
    return Problem(f"prob-draw-{i:03d}", "probability", "drawing without replacement", "evaluate",
                   f"A bag has {r} red and {tot - r} blue marbles. Two are drawn without replacement. "
                   f"What is the probability both are red?", expr, s(val), steps)


def expected_value(rng, i):
    a, b, c = rng.randint(3, 20), rng.randint(1, 8), rng.randint(1, 6)
    val = R(a, 6) + R(2 * b, 6) - R(3 * c, 6)
    expr = f"(1/6)*{a} + (2/6)*{b} + (3/6)*(-{c})"
    steps = [f"{a}/6 + {2*b}/6 - {3*c}/6", f"{a + 2*b - 3*c}/6", s(val)]
    return Problem(f"prob-ev-{i:03d}", "probability", "expected value", "evaluate",
                   f"Roll a fair die. You win ${a} on a 6, win ${b} on a 2 or 4, and lose ${c} on an odd number. "
                   f"What is the expected winnings?", expr, s(val), steps)


def at_least_one(rng, i):
    n = rng.randint(2, 5)
    val = 1 - R(5, 6)**n
    expr = f"1 - (5/6)**{n}"
    steps = [f"1 - {5**n}/{6**n}", f"({6**n} - {5**n})/{6**n}", s(val)]
    return Problem(f"prob-atl-{i:03d}", "probability", "complement rule", "evaluate",
                   f"A fair die is rolled {n} times. What is the probability of at least one six?", expr, s(val), steps)


TEMPLATES = [linear_one_side, linear_two_sides, quadratic, fractions, expand_difference,
             derivative_product, derivative_at_point, definite_integral, removable_limit,
             binomial_prob, without_replacement, expected_value, at_least_one]


def generate(per_template: int = 40, seed: int = 7) -> list[Problem]:
    rng = random.Random(seed)
    return [tpl(rng, i) for tpl in TEMPLATES for i in range(per_template)]


def save(problems: list[Problem], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(json.dumps(p.to_dict()) for p in problems) + "\n", encoding="utf-8")


def load(path: str | Path) -> list[Problem]:
    return [Problem(**json.loads(l)) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
