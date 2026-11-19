"""Models under evaluation.

* ``ClaudeModel``     - a real LLM via the Anthropic API (needs ANTHROPIC_API_KEY).
* ``SimulatedModel``  - offline stand-ins that start from the reference solution and
  inject realistic, typed reasoning errors at configurable rates. They exist so the
  whole pipeline (verification, statistics, dashboard) runs without API keys, and so
  the verifier can be checked against errors whose type and location are known.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

import sympy as sp

from .parsing import equivalent, has_rule_operator, parse, parse_answer_set, split_equals
from .problems import Problem


@dataclass
class Solution:
    steps: list[str]
    final_answer: str
    injected: dict | None = None   # ground truth for simulated errors (type, step)
    raw: str = ""


# ====================================================================== simulated
PROFILES = {
    # probability that a given attempt contains each error type
    "sim-careful":       {"arithmetic_slip": 0.04, "invalid_algebra": 0.03, "misapplied_rule": 0.03, "unjustified_leap": 0.02, "recover": 0.30},
    "sim-hasty":         {"arithmetic_slip": 0.15, "invalid_algebra": 0.06, "misapplied_rule": 0.05, "unjustified_leap": 0.10, "recover": 0.20},
    "sim-rule-confused": {"arithmetic_slip": 0.05, "invalid_algebra": 0.10, "misapplied_rule": 0.25, "unjustified_leap": 0.03, "recover": 0.50},
}


@dataclass
class SimulatedModel:
    name: str
    rates: dict = field(default_factory=dict)
    seed: int = 0

    @classmethod
    def from_profile(cls, name: str, seed: int = 0) -> "SimulatedModel":
        return cls(name, PROFILES[name], seed)

    def solve(self, problem: Problem) -> Solution:
        rng = random.Random(f"{self.name}|{problem.id}|{self.seed}")
        steps, answer = list(problem.reference_steps), problem.answer
        u, acc = rng.random(), 0.0
        for etype in ("arithmetic_slip", "invalid_algebra", "misapplied_rule", "unjustified_leap"):
            acc += self.rates.get(etype, 0.0)
            if u < acc:
                corrupted = _inject(etype, problem, rng)
                if corrupted is None:          # not applicable to this problem -> clean attempt
                    break
                steps, answer, idx = corrupted
                if etype != "unjustified_leap" and rng.random() < self.rates.get("recover", 0):
                    answer = problem.answer    # "knows" the answer anyway -> lucky guess
                return Solution(steps, answer, {"type": etype, "step": idx})
        return Solution(steps, answer)


def _inject(etype: str, p: Problem, rng: random.Random):
    ref = p.reference_steps
    if etype == "unjustified_leap":
        return ref[:1], _perturb_answer(p, rng), 1
    if p.kind == "solve":
        return _inject_solve(etype, p, rng)

    if etype == "misapplied_rule":
        m = p.meta.get("misapplied")
        if not m:
            return None
        i = m["index"]
        if equivalent(parse(m["text"]), parse(ref[i])):
            return None  # wrong rule happens to give the right value here (e.g. x**3 == x**2 at x = 1)
        return _finish_eval(ref[:i] + [m["text"]], i)

    prevs = [p.expression] + ref[:-1]
    candidates = []
    for i, (prev, cur) in enumerate(zip(prevs, ref)):
        if has_rule_operator(prev) and not has_rule_operator(cur):
            continue  # an error here would be a rule error, not this type
        if has_rule_operator(cur):
            # still inside an operator (e.g. product-rule setup): only a textual sign error fits
            if etype == "invalid_algebra" and " + " in cur:
                candidates.append(i)
            continue
        val = sp.sympify(parse(split_equals(cur)[-1])).doit()
        symbolic = bool(val.free_symbols)
        if etype == "arithmetic_slip" and not symbolic:
            candidates.append(i)
        if etype == "invalid_algebra" and symbolic and isinstance(sp.expand(val), sp.Add):
            candidates.append(i)
    if not candidates:
        return None
    i = rng.choice(candidates)
    if has_rule_operator(ref[i]):
        return _finish_eval(ref[:i] + [ref[i].replace(" + ", " - ", 1)], i)
    val = sp.sympify(parse(ref[i])).doit()
    if etype == "arithmetic_slip":
        bad = val + rng.choice([-2, -1, 1, 2]) if val.is_integer else val + sp.Rational(rng.choice([-1, 1]), sp.denom(val))
    else:
        terms = list(sp.expand(val).args)
        j = rng.randrange(len(terms))
        terms[j] = -terms[j]           # classic sign error on one term
        bad = sp.Add(*terms)
    return _finish_eval(ref[:i] + [sp.sstr(bad)], i)


def _finish_eval(steps: list[str], idx: int):
    val = sp.sympify(parse(steps[-1])).doit()
    simp = sp.sstr(sp.expand(sp.simplify(val)))
    if simp.replace(" ", "") != steps[-1].replace(" ", ""):
        steps = steps + [simp]
    return steps, simp, idx


def _inject_solve(etype: str, p: Problem, rng: random.Random):
    x = sp.Symbol(p.variable)
    ref = p.reference_steps
    if etype == "arithmetic_slip":
        i = rng.randrange(len(ref) - (1 if p.topic.startswith("quadratic") else 0))
        lhs, rhs = (parse(s) for s in split_equals(ref[i]))
        bad = f"{sp.sstr(lhs)} = {sp.sstr(rhs + rng.choice([-3, -2, -1, 1, 2, 3]))}"
    elif etype == "invalid_algebra" and p.topic.startswith("quadratic"):
        r1, r2 = (parse(v) for v in p.answer.split(","))
        i = len(ref) - 1
        if rng.random() < 0.5 and r1 != 0 and -r1 != r2:
            bad = f"{sp.sstr(sp.Mul(x + r1, x - r2, evaluate=False))} = 0"   # sign error when factoring
        else:
            bad = f"{sp.sstr(x - r1)} = 0"                                  # divided away a root
    else:
        return None
    lhs, rhs = (parse(s) for s in split_equals(bad))
    roots = [sp.nsimplify(r) for r in sp.solve(sp.Eq(lhs, rhs), x)]
    steps = ref[:i] + [bad]
    if len(roots) == 1 and not bad.replace(" ", "").startswith(f"{x}="):
        steps.append(f"x = {sp.sstr(roots[0])}")
    elif len(roots) == 2 and "*" not in bad.split("=")[0]:
        f = sp.factor(sp.expand(lhs - rhs))
        if isinstance(f, sp.Mul):
            steps.append(f"{sp.sstr(f)} = 0")
    return steps, ", ".join(sp.sstr(r) for r in roots), i


def _perturb_answer(p: Problem, rng: random.Random) -> str:
    if p.kind == "solve":
        vals = parse_answer_set(p.answer)
        vals[0] = vals[0] + rng.choice([-2, -1, 1, 2])
        return ", ".join(sp.sstr(v) for v in vals)
    val = parse(p.answer)
    delta = rng.choice([-1, 1]) if (val.is_integer or val.free_symbols) else sp.Rational(1, max(2, int(sp.denom(val))))
    return sp.sstr(val + delta)


# ====================================================================== real LLM
SYSTEM_PROMPT = """You are solving math problems. Show your work as a list of steps that a computer algebra system can check.

Rules for steps:
- Use SymPy syntax: * for multiplication, ** for powers, sqrt(), sin(), exp(), log(), binomial(n, k), Rational or a/b for fractions.
- For problems that ask you to compute a value or simplify: every step is an expression equal to the previous step (you may write 'a = b'). The first step should transform the original expression, the last step should be the simplified result.
- For problems that ask you to solve an equation: every step is an equation in x (exactly one '=') that has the same solutions as the previous one.
- Give the final answer in simplest exact form. For equations with several solutions, separate them with commas, e.g. "2, -3".
"""

SOLUTION_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {"type": "array", "items": {"type": "string"}},
        "final_answer": {"type": "string"},
    },
    "required": ["steps", "final_answer"],
    "additionalProperties": False,
}


class ClaudeModel:
    """Evaluates a Claude model through the Anthropic Messages API.

    Server-side refusal fallbacks are deliberately NOT enabled: a fallback would let a
    different model answer, which would contaminate the per-model comparison. A refusal
    is recorded as an unparseable attempt instead.
    """

    def __init__(self, model: str = "claude-opus-5-5", effort: str = "medium"):
        import anthropic

        self.client = anthropic.Anthropic()
        self.name = model
        self.effort = effort

    def solve(self, problem: Problem) -> Solution:
        response = self.client.messages.create(
            model=self.name,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            output_config={"effort": self.effort, "format": {"type": "json_schema", "schema": SOLUTION_SCHEMA}},
            messages=[{"role": "user", "content": problem.statement}],
        )
        if response.stop_reason == "refusal":
            return Solution([], "", raw="[refusal]")
        text = "".join(b.text for b in response.content if b.type == "text")
        try:
            data = json.loads(text)
            return Solution([str(s) for s in data["steps"]], str(data["final_answer"]), raw=text)
        except (json.JSONDecodeError, KeyError):
            return Solution([], "", raw=text)


def get_model(name: str):
    if name in PROFILES:
        return SimulatedModel.from_profile(name)
    if name.startswith("claude"):
        return ClaudeModel(name)
    raise ValueError(f"unknown model {name!r}; use one of {list(PROFILES)} or a Claude model id")
