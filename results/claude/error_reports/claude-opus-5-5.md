# Error report: claude-opus-5-5

1 attempts with at least one invalid step (showing up to 25).

### calc-int-004 (definite integral) - claude-opus-5-5

**Problem:** Evaluate the integral of -x**2 + 5*x - 5 from x = -2 to x = -1.

**Expected:** `-89/6`  |  **Model answer:** `-89/6`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `Integral(-x**2 + 5*x - 5, (x, -2, -1)) = [-x**3/3 + 5*x**2/2 - 5*x] evaluated from x = -2 to x = -1` | unreadable |
| 2 | `(-(-1)**3/3 + 5*(-1)**2/2 - 5*(-1)) - (-(-2)**3/3 + 5*(-2)**2/2 - 5*(-2))` | ok |
| 3 | `(1/3 + 5/2 + 5) - (8/3 + 10 + 10)` | ok |
| 4 | `47/6 - 68/3` | ok |
| 5 | `-89/6` | ok |

> Reasoning first breaks at step 1: **parse_error**.
