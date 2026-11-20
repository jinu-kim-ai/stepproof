# Error report: claude-haiku-5-5

1 attempts with at least one invalid step (showing up to 25).

### calc-int-006 (definite integral) - claude-haiku-5-5

**Problem:** Evaluate the integral of -2*x**2 + 4*x + 5 from x = 1 to x = 3.

**Expected:** `26/3`  |  **Model answer:** `23/3`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `integrate(-2*x**2 + 4*x + 5, (x, 1, 3))` | ok |
| 2 | `(-2*x**3/3 + 2*x**2 + 5*x).subs(x, 3) - (-2*x**3/3 + 2*x**2 + 5*x).subs(x, 1)` | ok |
| 3 | `15 - Rational(22, 3)` | **arithmetic_slip** - '15 - Rational(22, 3)' does not follow from '(-2*x**3/3 + 2*x**2 + 5*x).subs(x, 3) - (-2*x**3/3 + 2*x**2 + 5*x).subs(x, 1)': got 23/3, expected 26/3 |
| 4 | `Rational(23, 3)` | carries earlier error |

> Reasoning first breaks at step 3: **arithmetic_slip**.
