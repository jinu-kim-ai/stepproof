# StepProof: LLM Math Reasoning Evaluator

Most math benchmarks only check the **final answer**. StepProof checks **every intermediate step** with symbolic computation (SymPy). It reports *where* a model's reasoning breaks and *what kind* of mistake it made. Models are then compared with bootstrap confidence intervals instead of single accuracy numbers.

A real example, from Claude Haiku 5.5 on *"Evaluate the integral of -2x² + 4x + 5 from x = 1 to x = 3"* (step 2 is abbreviated here; the full output is in `results/claude/error_reports/`):

```
| Step | Content                                                  | Verdict |
|------|----------------------------------------------------------|---------|
| 1    | integrate(-2*x**2 + 4*x + 5, (x, 1, 3))                  | ok |
| 2    | (-2*x**3/3 + 2*x**2 + 5*x) at x = 3, minus the same at 1 | ok |
| 3    | 15 - 22/3                                                | arithmetic_slip - got 23/3, expected 26/3 |
| 4    | 23/3                                                     | carries earlier error |

> Reasoning first breaks at step 3: arithmetic_slip.
```

An answer-only benchmark reports "wrong". StepProof reports that the antiderivative and the setup were right, and that the model miscalculated F(1) as 22/3 instead of 19/3.

## What it does

- **Benchmark:** 520 competition-style problems from 13 templates across **algebra** (linear and quadratic equations, fractions, polynomial simplification), **calculus** (product rule, derivative at a point, definite integrals, limits) and **probability** (binomial, sampling without replacement, expected value, complement rule). Generation is deterministic (seeded), and every answer is computed by SymPy.
- **Step verifier:**
  - *Evaluate* problems: every step must follow from the previous one. It may equal it, or be the result of the operation the problem still requires: differentiate, take the limit, substitute the point, apply the bounds.
  - *Solve* problems: every equation must keep the same solution set. Following one branch of a factored equation is accepted when the final answer still reports every root.
  - A broken step is recorded once; later steps that correctly carry the error forward are marked `propagated`, not double-counted.
  - A step that can't be read as math is `parse_error`: skipped and reported as unreadable, never counted as wrong.
- **Error taxonomy:**

| Type | Detected when |
|---|---|
| `arithmetic_slip` | a numeric computation is wrong, or only an equation's constant term changed |
| `invalid_algebra` | a symbolic manipulation is not an equivalence: sign or term errors, or a lost or gained root |
| `misapplied_rule` | the step that evaluates a derivative, integral, limit or binomial gives the wrong result |
| `unjustified_leap` | the final answer does not follow from the last written step, or no work is shown |
| `parse_error` | the step can't be read as mathematics |

- **Metrics:**
  - *answer accuracy*, *process accuracy* (every step verified), *flawed* and *unreadable* rates, and *lucky-guess rate* (right answer, invalid reasoning);
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

Each run saves the model's own steps, so results can be re-checked after a verifier change without calling the API again:

```bash
python -m stepproof reverify --results results/claude
```

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

The injected errors are synthetic, though, and they are written in the same style as the reference solutions. Section 2 shows why that is not enough.

### 2. Real models: Claude Opus 5.5 and Claude Haiku 5.5

130 problems each (10 per template), 260 API requests. Raw outputs are in `results/claude/`.

| Model | Answer accuracy [95% CI] | Every step verified | Flawed step | Unreadable step |
|---|---|---|---|---|
| claude-opus-5-5 | 100% (130/130) | 99.2% | 0 | 1 |
| claude-haiku-5-5 | 99.2% (129/130) [97.7, 100] | 99.2% | 1 | 0 |

Paired bootstrap on answer accuracy: Haiku − Opus = −0.8% [−2.3, 0.0], **not significant**.

What this shows:

1. **The benchmark is too easy for these models.** One wrong answer in 260 attempts cannot separate them. With 0 errors in 130, the 95% upper bound on Opus's true error rate is still about 2.3% (rule of three); the bootstrap interval collapses to a point only because there is no variance to resample. Harder templates are the next step.
2. **The one real error was located exactly.** It is the integral shown at the top of this README: the verifier accepted the setup and flagged the single miscalculated step.
3. **The first pass over these outputs was wrong, and the verifier was at fault.** It flagged 20% of Haiku's attempts and 13% of Opus's as flawed while their answers were 99–100% correct. Reading the flagged attempts, and a six-problem trial before the run, showed all but one were valid work in a notation the verifier did not expect:

| What the model wrote | Why it is valid | Fix |
|---|---|---|
| `(x**2 - 64)/(x + 8)` → `x - 8` → `-16` for a limit | simplifies the function first, then takes the limit | steps may equal the current function *or* the result of the pending operation |
| `f'(x) = 12*x**2 + 12*x - 5`, then `f'(1) = 19` | `f'(x)` is a label, not math to check | labels are dropped before parsing |
| `Substitute x = 1: -3*1**2 - 4*1 - 1` | prose prefix | text before a colon is dropped |
| `(x - 6)*(x + 2) = 0` → `x - 6 = 0`, answer `6, -2` | follows one case of a factored equation | a branch is accepted when the final answer keeps every root |

After the fixes, the saved outputs were re-checked offline with `reverify`. The injected-error check in section 1 still passes at 100% with 0 false alarms, and each pattern above is now a regression test. The lesson: a grader validated only on synthetic errors can still be badly wrong on real output.

Cost of the run: 135,442 input and 38,570 output tokens, about $0.54 at list prices at the time.

### 3. Comparing models (simulated)

The three built-in models are **simulated**. Each starts from the reference solution and injects typed errors at a different rate profile, so the full pipeline runs offline with known ground truth. They are not real LLM results; they exist to exercise the statistics on models that do make errors.

| Model | Answer acc [95% CI] | Process acc [95% CI] | Lucky guess |
|---|---|---|---|
| sim-careful | 92.3% [90.0, 94.4] | 90.6% [88.1, 92.9] | 1.7% |
| sim-hasty | 80.0% [76.7, 83.5] | 77.7% [74.2, 81.3] | 2.3% |
| sim-rule-confused | 89.0% [86.3, 91.7] | 80.4% [76.9, 83.7] | 8.7% |

Paired bootstrap on answer accuracy: *sim-careful vs sim-rule-confused* differ by **+3.3% [−0.2, +6.9], p = 0.07, which is not significant**. Their **process** accuracy differs by about 10 points, though: sim-rule-confused often reaches correct answers through invalid steps, like this attempt:

```
Problem: Solve for x: 3*x - 15 = 18        Expected: 11    Model answer: 11

| Step  | Content    | Verdict |
|-------|------------|---------|
| 1     | 3*x = 31   | arithmetic_slip - solutions changed from {11} to {31/3} |
| 2     | x = 31/3   | carries earlier error |
| final | 11         | unjustified_leap - does not follow from last step 'x = 31/3' |
```

An answer-only benchmark would score that attempt as correct. This is the gap that answer-only grading hides.

## Project layout

```
stepproof/
  problems.py  seeded problem generator (13 templates, reference solutions)
  parsing.py   safe SymPy parsing (whitelisted names only), equivalence checks
  verifier.py  step-by-step verification + error classification
  models.py    Claude API model + simulated models with typed error injection
  runner.py    run models over the benchmark; re-verify saved runs offline
  stats.py     bootstrap CI, paired bootstrap
  report.py    summaries, model comparisons, markdown error reports
  __main__.py  CLI
app.py         Streamlit dashboard
tests/
```

## Limitations

- The problems are too easy to separate current frontier models (section 2). Real-model results cover 130 of the 520 problems and two models from one provider.
- Steps must be written as SymPy-parsable math. Prose steps ("by symmetry...") come out as `parse_error` and are reported as unreadable.
- The notation fixes in section 2 came from two models' outputs. Other models will write steps in ways not yet handled.
- Verification is value- and solution-set-based. A step with the right value for the wrong reason (for example, at x = 1) is accepted.
- Error-type classification is heuristic. For linear equations, a mis-moved term and a miscalculated constant look identical, so both are reported as `arithmetic_slip`.
