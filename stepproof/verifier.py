"""Step-by-step symbolic verification of a model's solution.

Two problem kinds:

* ``evaluate`` - every step is an expression (or an ``a = b = c`` chain) that must
  follow from the previous one: either equal to it, or the result of applying the
  operation the problem still requires (differentiate, take the limit, substitute
  the point, apply the bounds). Labels such as ``f'(x) =`` and prose prefixes such
  as ``Substitute x = 1:`` are ignored.
* ``solve``    - every step is an equation in the unknown; each step must have the
  same solution set as the previous equation (an equivalence-preserving move), or
  follow one branch of it when the final answer still reports every root.

A step that cannot be read as mathematics is ``parse_error``: it is skipped, not
counted as wrong, and the steps after it are still checked.

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
from typing import Callable

import sympy as sp

from .parsing import (
    ParseError, equation_poly, equivalent, has_rule_operator, parse, parse_answer_set,
    same_set, solution_set, step_parts, strip_prose,
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
        """Right final answer reached through flawed reasoning (an unreadable step is not a flaw)."""
        return self.final_correct and self.first_error_type not in (None, "parse_error")

    def to_dict(self) -> dict:
        return asdict(self)


def verify(problem: Problem, steps: list[str], final_answer: str) -> Verification:
    if problem.kind == "evaluate":
        results, state = _verify_evaluate(problem, steps)
    else:
        results, state = _verify_solve(problem, steps, final_answer)
    final_correct = _final_correct(problem, final_answer)

    # Final-answer consistency with what the written steps derive (unjustified leap check)
    leap = _leap_check(problem, steps, final_answer, results, state)
    if leap:
        results.append(leap)

    # A real error outranks an unreadable step: unreadable means "could not check", not "wrong".
    first = next((r for r in results if r.status == "error"), None) or \
        next((r for r in results if r.status == "parse_error"), None)
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
@dataclass
class _Transition:
    """One operation the problem still requires, e.g. differentiate, then substitute x = 2."""
    name: str
    forward: Callable                 # value before the operation -> value after it
    is_rule: bool = True              # a calculus rule (True) or plain evaluation at a point (False)
    check: Callable | None = None     # looser single-step test (an antiderivative is only fixed up to a constant)


def _plan(expr) -> tuple[sp.Expr, list[_Transition]]:
    """Split a problem into the function being worked on and the operations still to apply.

    Solvers rarely restate the whole problem on every line. For ``lim (x**2 - 64)/(x + 8)`` they
    simplify the *function* to ``x - 8`` and only then take the limit. So a step may equal the
    current object, or the result of applying the next operation(s) to it.
    """
    if isinstance(expr, sp.Limit):
        g, v, a = expr.args[0], expr.args[1], expr.args[2]
        return g, [_Transition("taking the limit", lambda h: sp.limit(h, v, a))]
    if isinstance(expr, sp.Subs) and isinstance(expr.expr, sp.Derivative) and len(expr.variables) == 1:
        v, p = expr.variables[0], expr.point[0]
        return expr.expr.expr, [
            _Transition("differentiating", lambda h: sp.diff(h, v)),
            _Transition("substituting", lambda h: sp.sympify(h).subs(v, p), is_rule=False),
        ]
    if isinstance(expr, sp.Derivative) and len(expr.variables) == 1:
        v = expr.variables[0]
        return expr.expr, [_Transition("differentiating", lambda h: sp.diff(h, v))]
    if isinstance(expr, sp.Integral) and len(expr.limits) == 1 and len(expr.limits[0]) == 3:
        v, a, b = expr.limits[0]
        return expr.function, [
            _Transition("integrating", lambda h: sp.integrate(h, v),
                        check=lambda h, s: bool(sp.sympify(s).free_symbols) and equivalent(sp.diff(s, v), h)),
            _Transition("applying the bounds", lambda F: sp.sympify(F).subs(v, b) - sp.sympify(F).subs(v, a),
                        is_rule=False),
        ]
    return expr, []


def _unwrap(val, transitions: list[_Transition], stage: int):
    """If a step re-states the pending operator around an expression, return that inner expression.

    ``Limit(x - 8, x, -8)`` written before the limit is taken says "the function is now x - 8".
    """
    pending = [t.name for t in transitions[stage:]]
    if not pending:
        return None
    if pending[0] == "taking the limit" and isinstance(val, sp.Limit):
        return val.args[0]
    if pending[0] == "differentiating":
        if isinstance(val, sp.Subs) and isinstance(val.expr, sp.Derivative):
            return val.expr.expr
        if isinstance(val, sp.Derivative):
            return val.expr
    if pending[0] == "substituting" and isinstance(val, sp.Subs):
        return val.expr
    if pending[0] == "integrating" and isinstance(val, sp.Integral):
        return val.function
    return None


def _match(prev, val, transitions: list[_Transition], stage: int) -> int | None:
    """The stage ``val`` reaches from ``prev`` (same stage, or after the next operations), else None."""
    if equivalent(prev, val):
        return stage
    cur = prev
    for k in range(stage, len(transitions)):
        tr = transitions[k]
        try:
            if k == stage and tr.check and tr.check(prev, val):
                return k + 1
            cur = tr.forward(cur)
        except Exception:        # SymPy could not apply the operation to a malformed value
            return None
        if equivalent(cur, val):
            return k + 1
    return None


def _verify_evaluate(problem: Problem, steps: list[str]):
    prev, transitions = _plan(parse(problem.expression))
    stage = 0
    prev_text = problem.expression
    out: list[StepResult] = []
    broken = False
    for i, step in enumerate(steps):
        status, etype, detail = "ok", None, ""
        try:
            for part in step_parts(step):
                val = parse(part)
                inner = _unwrap(val, transitions, stage)
                if inner is not None:
                    val, reached = inner, (stage if equivalent(prev, inner) else None)
                else:
                    val = sp.sympify(val).doit()
                    reached = _match(prev, val, transitions, stage)
                if reached is not None:
                    stage = reached
                else:
                    kind = _classify_eval(prev_text, part, prev, val, transitions, stage)
                    if status == "ok":
                        status, etype = "error", kind
                        detail = _explain(prev_text, part, prev, val, transitions, stage)
                    if kind == "misapplied_rule" and inner is None and stage < len(transitions):
                        stage += 1      # the rule was attempted; later steps continue from its (wrong) result
                prev_text, prev = part, val
        except ParseError as exc:
            # unreadable: skip it and keep checking the following steps against the last readable one
            out.append(StepResult(i, step, "parse_error", "parse_error", str(exc)))
            continue
        if status == "ok" and broken:
            status = "propagated"
        broken = broken or status == "error"
        out.append(StepResult(i, step, status, etype, detail))
    return out, (prev, transitions, stage)


def _classify_eval(prev_text: str, cur_text: str, prev_val, cur_val, transitions, stage: int) -> str:
    if has_rule_operator(prev_text):
        # operator evaluated in this step -> wrong rule; still present -> bad manipulation inside it
        return "misapplied_rule" if not has_rule_operator(cur_text) else "invalid_algebra"
    if has_rule_operator(cur_text):
        return "invalid_algebra"
    numeric_now = not sp.sympify(cur_val).free_symbols
    if stage < len(transitions):
        if transitions[stage].is_rule:
            return "misapplied_rule"            # the step applies the pending rule and gets it wrong
        if numeric_now:
            return "arithmetic_slip"            # plugged in the point / bounds and miscalculated
    numeric = not sp.sympify(prev_val).doit().free_symbols and numeric_now
    return "arithmetic_slip" if numeric else "invalid_algebra"


def _explain(prev_text, cur_text, prev_val, cur_val, transitions, stage: int) -> str:
    expected = _show(prev_val)
    if stage < len(transitions):
        try:
            expected += f", or {_show(transitions[stage].forward(prev_val))} after {transitions[stage].name}"
        except Exception:
            pass
    return f"'{cur_text.strip()}' does not follow from '{prev_text.strip()}': got {_show(cur_val)}, expected {expected}"


# ---------------------------------------------------------------- solve problems
def _verify_solve(problem: Problem, steps: list[str], final_answer: str) -> tuple[list[StepResult], list]:
    """Returns the per-step results and the solution set the final answer must follow from.

    Case analysis: after ``(x - 6)*(x + 2) = 0`` a solver may continue with one branch,
    ``x - 6 = 0``. Such a step keeps only *some* of the roots. It is accepted as a case when
    the final answer still reports every root; if the final answer drops the other roots,
    the same step is where a root was lost (invalid algebra, e.g. dividing by x).
    """
    var = sp.Symbol(problem.variable)
    out: list[StepResult] = []
    prev_eq = problem.expression
    prev_sols = list(solution_set(prev_eq, var))
    broken = False
    cases: list[int] = []          # indexes into `out` of steps that follow only one branch
    case_union: list = []
    for i, step in enumerate(steps):
        try:
            sols = list(solution_set(strip_prose(step), var))
        except (ParseError, NotImplementedError) as exc:
            out.append(StepResult(i, step, "parse_error", "parse_error", str(exc)))
            continue
        if same_set(prev_sols, sols):
            out.append(StepResult(i, step, "propagated" if broken else "ok"))
            prev_eq = step
        elif sols and len(sols) < len(prev_sols) and _subset(sols, prev_sols):
            cases.append(len(out))
            case_union += [s for s in sols if not _subset([s], case_union)]
            out.append(StepResult(i, step, "propagated" if broken else "ok",
                                  detail=f"case: one branch of {_fmt_set(prev_sols)}"))
        else:
            etype = _classify_solve(prev_eq, step, prev_sols, sols, var)
            detail = f"solutions changed from {_fmt_set(prev_sols)} to {_fmt_set(sols)}"
            out.append(StepResult(i, step, "error", etype, detail))
            broken = True
            prev_eq, prev_sols, cases, case_union = step, sols, [], []

    if cases:
        try:
            all_roots_reported = same_set(parse_answer_set(final_answer), prev_sols)
        except ParseError:
            all_roots_reported = False
        if not all_roots_reported:      # the other roots were never recovered -> they were lost here
            first = out[cases[0]]
            first.status, first.error_type = "error", "invalid_algebra"
            first.detail = f"solutions changed from {_fmt_set(prev_sols)} to {_fmt_set(case_union)} (lost a root)"
            for j in cases[1:]:
                out[j].status, out[j].detail = "propagated", ""
            return out, case_union
    return out, prev_sols


def _subset(a, b) -> bool:
    return all(any(equivalent(p, q) for q in b) for p in a)


def _classify_solve(prev_eq, cur_eq, prev_sols, sols, var) -> str:
    if len(sols) != len(prev_sols):
        return "invalid_algebra"  # lost or gained a root (e.g. divided by x)
    try:
        p, q = equation_poly(prev_eq, var), equation_poly(cur_eq, var)
    except ParseError:
        return "invalid_algebra"
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
        return equivalent(parse(step_parts(final_answer)[-1]), parse(problem.answer))
    except (ParseError, IndexError):
        return False


def _leap_check(problem, steps, final_answer, results, state) -> StepResult | None:
    """``state`` is what the written steps derived: a solution set (solve) or (value, operations, stage)."""
    idx = len(steps)
    if not steps:
        return StepResult(idx, final_answer, "error", "unjustified_leap", "final answer given with no supporting steps")
    if results and results[-1].status == "parse_error":
        return None
    try:
        if problem.kind == "solve":
            consistent = same_set(parse_answer_set(final_answer), state)
        else:
            prev, transitions, stage = state
            final_val = sp.sympify(parse(step_parts(final_answer)[-1])).doit()
            consistent = _match(prev, final_val, transitions, stage) is not None
    except (ParseError, NotImplementedError, IndexError):
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
