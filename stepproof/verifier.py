"""Step-by-step symbolic verification of a model's solution.

Two problem kinds:

* ``evaluate`` - every step is an expression (or an ``a = b = c`` chain) that must
  equal the previous one. Step 0 is compared with the problem's expression.
* ``solve``    - every step is an equation in the unknown; each step must have the
  same solution set as the previous equation (an equivalence-preserving move).

When a step breaks the chain we record *where* and *what kind* of error it is,
then keep verifying later steps against the broken value, so an early mistake is
reported once (``error``) and later steps that merely carry it forward are marked
``propagated`` rather than double-counted.

Error taxonomy
  arithmetic_slip    numeric computation wrong (or only the constant term of an equation changed)
  invalid_algebra    symbolic manipulation that is not an equivalence (sign/term errors, lost or gained roots)
  misapplied_rule    a step that evaluates a derivative / integral / limit / binomial ... gives the wrong result
  unjustified_leap   final answer does not follow from the last written step (or no work shown)
  parse_error        step could not be read as mathematics
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

import sympy as sp

from .parsing import (
    ParseError, equation_poly, equivalent, has_rule_operator, parse, parse_answer_set,
    same_set, solution_set, split_equals,
)
from .problems import Problem

ERROR_TYPES = ["arithmetic_slip", "invalid_algebra", "misapplied_rule", "unjustified_leap", "parse_error"]


@dataclass
class StepResult:
    index: int            # -1 = the problem statement, len(steps) = final answer
    text: str
    status: str           # ok | error | propagated | parse_error
    error_type: str | None = None
    detail: str = ""


@dataclass
class Verification:
    problem_id: str
    final_correct: bool
    process_correct: bool
    first_error_step: int | None
    first_error_type: str | None
    steps: list[StepResult] = field(default_factory=list)
    final_answer: str = ""
    expected_answer: str = ""

    @property
    def lucky_guess(self) -> bool:
        """Right final answer reached through flawed reasoning."""
        return self.final_correct and not self.process_correct

    def to_dict(self) -> dict:
        return asdict(self)


def verify(problem: Problem, steps: list[str], final_answer: str) -> Verification:
    results = _verify_evaluate(problem, steps) if problem.kind == "evaluate" else _verify_solve(problem, steps)
    final_correct = _final_correct(problem, final_answer)

    # Final-answer consistency with the last written step (unjustified leap check)
    leap = _leap_check(problem, steps, final_answer, results)
    if leap:
        results.append(leap)

    first = next((r for r in results if r.status in ("error", "parse_error")), None)
    return Verification(
        problem_id=problem.id,
        final_correct=final_correct,
        process_correct=first is None,
        first_error_step=first.index if first else None,
        first_error_type=first.error_type if first else None,
        steps=results,
        final_answer=final_answer,
        expected_answer=problem.answer,
    )


# ---------------------------------------------------------------- evaluate problems
def _verify_evaluate(problem: Problem, steps: list[str]) -> list[StepResult]:
    out: list[StepResult] = []
    prev_text = problem.expression
    prev_val = parse(problem.expression)
    broken = False
    for i, step in enumerate(steps):
        parts = split_equals(step)
        status, etype, detail = "ok", None, ""
        try:
            for part in parts:
                val = parse(part)
                if not equivalent(prev_val, val):
                    if status == "ok":
                        etype = _classify_eval(prev_text, part, prev_val, val)
                        status = "error"
                        detail = f"'{prev_text.strip()}' != '{part.strip()}' ({_show(prev_val)} vs {_show(val)})"
                prev_text, prev_val = part, val
        except ParseError as exc:
            out.append(StepResult(i, step, "parse_error", "parse_error", str(exc)))
            broken = True
            continue
        if status == "ok" and broken:
            status = "propagated"
        broken = broken or status == "error"
        out.append(StepResult(i, step, status, etype, detail))
    return out


def _classify_eval(prev_text: str, cur_text: str, prev_val, cur_val) -> str:
    if has_rule_operator(prev_text):
        # operator evaluated in this step -> wrong rule; still present -> bad manipulation inside it
        return "misapplied_rule" if not has_rule_operator(cur_text) else "invalid_algebra"
    numeric = not sp.sympify(prev_val).doit().free_symbols and not sp.sympify(cur_val).free_symbols
    return "arithmetic_slip" if numeric else "invalid_algebra"


# ---------------------------------------------------------------- solve problems
def _verify_solve(problem: Problem, steps: list[str]) -> list[StepResult]:
    var = sp.Symbol(problem.variable)
    out: list[StepResult] = []
    prev_eq = problem.expression
    prev_sols = solution_set(prev_eq, var)
    broken = False
    for i, step in enumerate(steps):
        try:
            sols = solution_set(step, var)
        except (ParseError, NotImplementedError) as exc:
            out.append(StepResult(i, step, "parse_error", "parse_error", str(exc)))
            broken = True
            continue
        if same_set(prev_sols, sols):
            out.append(StepResult(i, step, "propagated" if broken else "ok"))
        else:
            etype = _classify_solve(prev_eq, step, prev_sols, sols, var)
            detail = f"solutions changed from {_fmt_set(prev_sols)} to {_fmt_set(sols)}"
            out.append(StepResult(i, step, "error", etype, detail))
            broken = True
        prev_eq, prev_sols = step, sols
    return out


def _classify_solve(prev_eq, cur_eq, prev_sols, sols, var) -> str:
    if len(sols) != len(prev_sols):
        return "invalid_algebra"  # lost or gained a root (e.g. divided by x)
    p, q = equation_poly(prev_eq, var), equation_poly(cur_eq, var)
    if p is None or q is None or p.degree() != q.degree():
        return "invalid_algebra"
    # Only the constant term disagrees (non-constant parts proportional) -> arithmetic slip
    pc, qc = p.all_coeffs()[:-1], q.all_coeffs()[:-1]
    ratio = None
    for a, b in zip(pc, qc):
        if a == 0 and b == 0:
            continue
        if a == 0 or b == 0:
            return "invalid_algebra"
        r = sp.nsimplify(b / a)
        if ratio is None:
            ratio = r
        elif sp.simplify(r - ratio) != 0:
            return "invalid_algebra"
    return "arithmetic_slip"


# ---------------------------------------------------------------- final answer
def _final_correct(problem: Problem, final_answer: str) -> bool:
    try:
        if problem.kind == "solve":
            return same_set(parse_answer_set(final_answer), parse_answer_set(problem.answer))
        return equivalent(parse(final_answer), parse(problem.answer))
    except ParseError:
        return False


def _leap_check(problem, steps, final_answer, results) -> StepResult | None:
    idx = len(steps)
    if not steps:
        return StepResult(idx, final_answer, "error", "unjustified_leap", "final answer given with no supporting steps")
    if results and results[-1].status == "parse_error":
        return None
    try:
        if problem.kind == "solve":
            var = sp.Symbol(problem.variable)
            consistent = same_set(parse_answer_set(final_answer), solution_set(steps[-1], var))
        else:
            consistent = equivalent(parse(split_equals(steps[-1])[-1]), parse(final_answer))
    except (ParseError, NotImplementedError):
        return StepResult(idx, final_answer, "parse_error", "parse_error", "could not parse final answer")
    if consistent:
        return None
    return StepResult(idx, final_answer, "error", "unjustified_leap",
                      f"final answer '{final_answer}' does not follow from last step '{steps[-1]}'")


def _show(v) -> str:
    try:
        v = sp.sympify(v).doit()
        return str(sp.nsimplify(v)) if not v.free_symbols else str(sp.simplify(v))
    except Exception:
        return str(v)


def _fmt_set(s) -> str:
    return "{" + ", ".join(str(v) for v in s) + "}"
