# StepProof: LLM Math Reasoning Evaluator

Most math benchmarks only check the **final answer**. StepProof checks **every intermediate step** with symbolic computation (SymPy). It reports *where* a model's reasoning breaks and *what kind* of mistake it made. Models are then compared with bootstrap confidence intervals instead of single accuracy numbers.

```
| Step | Content                                                    | Verdict |
|------|------------------------------------------------------------|---------|
| 1    | Derivative(x**2, x)*log(x) + x**2*Derivative(log(x), x)    | ok |
| 2    | 2*x*1/x                                                    | misapplied_rule - expected x*(2*log(x) + 1), got 2 |
| 3    | 2                                                          | carries earlier error |
| final| 2*x*log(x) + x                                             | unjustified_leap - does not follow from last step '2' |

> Reasoning first breaks at step 2: misapplied_rule.
> Final answer is correct, but the written reasoning does not support it (lucky guess).
```

An answer-only benchmark would score that attempt as **correct**.

## What it does

- **Benchmark:** 520 competition-style problems from 13 templates across **algebra** (linear and quadratic equations, fractions, polynomial simplification), **calculus** (product rule, derivative at a point, definite integrals, limits) and **probability** (binomial, sampling without replacement, expected value, complement rule). Generation is deterministic (seeded), and every answer is computed by SymPy.
- **Step verifier:**
  - *Evaluate* problems: every step must be equal to the previous one.
  - *Solve* problems: every equation must keep the same solution set.
  - A broken step is recorded once; later steps that correctly carry the error forward are marked `propagated`, not double-counted.
- **Error taxonomy:**

| Type | Detected when |
|---|---|
| `arithmetic_slip` | a numeric computation is wrong, or only an equation's constant term changed |
| `invalid_algebra` | a symbolic manipulation is not an equivalence: sign or term errors, or a lost or gained root |
| `misapplied_rule` | the step that evaluates a derivative, integral, limit or binomial gives the wrong result |
| `unjustified_leap` | the final answer does not follow from the last written step, or no work is shown |
| `parse_error` | the step can't be read as mathematics |

- **Metrics:**
  - *answer accuracy*, *process accuracy* (every step valid), and *lucky-guess rate* (right answer, invalid reasoning);
  - per-domain breakdowns;
  - 95% **bootstrap confidence intervals**;
  - **paired bootstrap** tests between models. Problems are resampled jointly, so problem difficulty is shared.
- **Evidence-grounded error reports:** one markdown file per model (`results/error_reports/`) showing the exact failing step and why.
- **Interactive Streamlit dashboard:** accuracy with CIs, domain and topic breakdowns, error-type distribution, pairwise significance, and a step-by-step drill-down into any failed attempt.

## Quick start

```bash
pip install -r requirements.txt

python -m stepproof generate                 # data/problems.jsonl (520 problems)
python -m stepproof check-verifier           # validate the verifier on injected errors
python -m stepproof run                      # evaluate the built-in simulated models
streamlit run app.py                         # dashboard

pytest -q
```

### Evaluating real models (Claude)

```bash
export ANTHROPIC_API_KEY=...                 # or: ant auth login
python -m stepproof run --models claude-opus-5-5 claude-haiku-5-5 --limit 10 --workers 8 --out results/claude
streamlit run app.py                         # then point "Results file" to results/claude/results.jsonl
```

`--limit 10` uses 10 problems per template (130 total) to keep API cost down. Drop it to run all 520. Models are asked for JSON `{"steps": [...], "final_answer": ...}` via structured outputs. Refusal fallbacks are deliberately **off**, so every answer in a model's column really comes from that model. To add another provider, implement a class with a `.solve(problem) -> Solution` method in `stepproof/models.py`.

## Results

### 1. Is the verifier itself correct?

Before trusting a grader, test it. `check-verifier` injects every applicable error type into every problem, at a known step, and checks whether the verifier finds it:

| Injected error | Cases | Detected | Correct step | Correct type |
|---|---|---|---|---|
| arithmetic_slip | 443 | 100% | 100% | 100% |
| invalid_algebra | 131 | 100% | 100% | 100% |
| misapplied_rule | 180 | 100% | 100% | 100% |
| unjustified_leap | 520 | 100% | 100% | 100% |

**False alarms on the 520 correct reference solutions: 0.**

Building this check exposed real issues, which are now fixed:
- Sign errors *inside* an unevaluated `Limit(...)` were classified as arithmetic slips.
- Some "wrong rules" give the right number by coincidence. For example, the power rule without lowering the exponent gives the right value at x = 1, and nPk = nCk when k = 1. No value-based checker can see those, so they are excluded from the injection test.

The injected errors are synthetic, though. Real LLM output is messier (notation, skipped steps), so expect more `parse_error`s on real models.

### 2. Comparing models (simulated)

The three built-in models are **simulated**. Each starts from the reference solution and injects typed errors at a different rate profile, so the full pipeline runs offline with known ground truth. They are not real LLM results.

| Model | Answer acc [95% CI] | Process acc [95% CI] | Lucky guess |
|---|---|---|---|
| sim-careful | 92.3% [90.0, 94.4] | 90.6% [88.1, 92.9] | 1.7% |
| sim-hasty | 80.0% [76.7, 83.5] | 77.3% [73.8, 81.0] | 2.7% |
| sim-rule-confused | 89.0% [86.3, 91.7] | 80.2% [76.7, 83.7] | 8.8% |

Paired bootstrap on answer accuracy: *sim-careful vs sim-rule-confused* differ by **+3.3% [−0.2, +6.9], p = 0.07, which is not significant**. Their **process** accuracy differs by more than 10 points, though: sim-rule-confused often reaches correct answers through invalid steps. This is the gap that answer-only grading hides.

## Project layout

```
stepproof/
  problems.py  seeded problem generator (13 templates, reference solutions)
  parsing.py   safe SymPy parsing (whitelisted names only), equivalence checks
  verifier.py  step-by-step verification + error classification
  models.py    Claude API model + simulated models with typed error injection
  runner.py    run models over the benchmark
  stats.py     bootstrap CI, paired bootstrap
  report.py    summaries, model comparisons, markdown error reports
  __main__.py  CLI
app.py         Streamlit dashboard
tests/
```

## Limitations

- Steps must be written as SymPy-parsable math. Prose steps ("by symmetry...") come out as `parse_error`.
- Verification is value- and solution-set-based. A step with the right value for the wrong reason (for example, at x = 1) is accepted.
- Error-type classification is heuristic. For linear equations, a mis-moved term and a miscalculated constant look identical, so both are reported as `arithmetic_slip`.
