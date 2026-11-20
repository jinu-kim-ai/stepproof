# Error report: sim-rule-confused

102 attempts with at least one invalid step (showing up to 25).

### alg-lin1-002 (linear equation) - sim-rule-confused

**Problem:** Solve for x: 3*x + 14 = 47

**Expected:** `11`  |  **Model answer:** `13`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `3*x = 33` | ok |
| final answer | `13` | **unjustified_leap** - final answer '13' does not follow from last step '3*x = 33' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-lin1-014 (linear equation) - sim-rule-confused

**Problem:** Solve for x: 6*x - 11 = -23

**Expected:** `-2`  |  **Model answer:** `1`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `6*x = -12` | ok |
| 2 | `x = 1` | **arithmetic_slip** - solutions changed from {-2} to {1} |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-lin1-034 (linear equation) - sim-rule-confused

**Problem:** Solve for x: 7*x + 11 = 39

**Expected:** `4`  |  **Model answer:** `27/7`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `7*x = 27` | **arithmetic_slip** - solutions changed from {4} to {27/7} |
| 2 | `x = 27/7` | carries earlier error |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-lin1-036 (linear equation) - sim-rule-confused

**Problem:** Solve for x: 3*x - 15 = 18

**Expected:** `11`  |  **Model answer:** `11`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `3*x = 31` | **arithmetic_slip** - solutions changed from {11} to {31/3} |
| 2 | `x = 31/3` | carries earlier error |
| final answer | `11` | **unjustified_leap** - final answer '11' does not follow from last step 'x = 31/3' |

> Reasoning first breaks at step 1: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-lin2-007 (linear equation (both sides)) - sim-rule-confused

**Problem:** Solve for x: 6*x + 4 = 4*x + 2

**Expected:** `-1`  |  **Model answer:** `-1`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `2*x = -1` | **arithmetic_slip** - solutions changed from {-1} to {-1/2} |
| 2 | `x = -1/2` | carries earlier error |
| final answer | `-1` | **unjustified_leap** - final answer '-1' does not follow from last step 'x = -1/2' |

> Reasoning first breaks at step 1: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-lin2-008 (linear equation (both sides)) - sim-rule-confused

**Problem:** Solve for x: 5*x - 9 = -5*x - 109

**Expected:** `-10`  |  **Model answer:** `-10`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `10*x = -103` | **arithmetic_slip** - solutions changed from {-10} to {-103/10} |
| 2 | `x = -103/10` | carries earlier error |
| final answer | `-10` | **unjustified_leap** - final answer '-10' does not follow from last step 'x = -103/10' |

> Reasoning first breaks at step 1: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-lin2-009 (linear equation (both sides)) - sim-rule-confused

**Problem:** Solve for x: 4*x - 6 = 48 - 2*x

**Expected:** `9`  |  **Model answer:** `9`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `6*x = 54` | ok |
| 2 | `x = 7` | **arithmetic_slip** - solutions changed from {9} to {7} |
| final answer | `9` | **unjustified_leap** - final answer '9' does not follow from last step 'x = 7' |

> Reasoning first breaks at step 2: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-lin2-030 (linear equation (both sides)) - sim-rule-confused

**Problem:** Solve for x: 6*x - 4 = 126 - 7*x

**Expected:** `10`  |  **Model answer:** `11`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `13*x = 130` | ok |
| final answer | `11` | **unjustified_leap** - final answer '11' does not follow from last step '13*x = 130' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-lin2-035 (linear equation (both sides)) - sim-rule-confused

**Problem:** Solve for x: 5*x + 2 = 7*x - 4

**Expected:** `3`  |  **Model answer:** `4`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `-2*x = -8` | **arithmetic_slip** - solutions changed from {3} to {4} |
| 2 | `x = 4` | carries earlier error |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-lin2-039 (linear equation (both sides)) - sim-rule-confused

**Problem:** Solve for x: 7*x - 14 = -7*x - 84

**Expected:** `-5`  |  **Model answer:** `-5`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `14*x = -70` | ok |
| 2 | `x = -7` | **arithmetic_slip** - solutions changed from {-5} to {-7} |
| final answer | `-5` | **unjustified_leap** - final answer '-5' does not follow from last step 'x = -7' |

> Reasoning first breaks at step 2: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-quad-001 (quadratic equation) - sim-rule-confused

**Problem:** Solve for x (give all real solutions): x**2 + 2*x - 3 = 0

**Expected:** `-3, 1`  |  **Model answer:** `1, 3`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 + 2*x = 3` | ok |
| 2 | `(x - 3)*(x - 1) = 0` | **invalid_algebra** - solutions changed from {1, -3} to {1, 3} |

> Reasoning first breaks at step 2: **invalid_algebra**.

### alg-quad-011 (quadratic equation) - sim-rule-confused

**Problem:** Solve for x (give all real solutions): x**2 + 9*x + 20 = 0

**Expected:** `-4, -5`  |  **Model answer:** `-6, -3`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 + 9*x = -18` | **arithmetic_slip** - solutions changed from {-5, -4} to {-6, -3} |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-quad-016 (quadratic equation) - sim-rule-confused

**Problem:** Solve for x (give all real solutions): x**2 - 3*x - 40 = 0

**Expected:** `8, -5`  |  **Model answer:** `8, -5`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 - 3*x = 40` | ok |
| 2 | `(x + 5)*(x + 8) = 0` | **invalid_algebra** - solutions changed from {8, -5} to {-8, -5} |
| final answer | `8, -5` | **unjustified_leap** - final answer '8, -5' does not follow from last step '(x + 5)*(x + 8) = 0' |

> Reasoning first breaks at step 2: **invalid_algebra**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-quad-026 (quadratic equation) - sim-rule-confused

**Problem:** Solve for x (give all real solutions): x**2 + 13*x + 40 = 0

**Expected:** `-5, -8`  |  **Model answer:** `-13/2 - sqrt(5)/2, -13/2 + sqrt(5)/2`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 + 13*x = -41` | **arithmetic_slip** - solutions changed from {-8, -5} to {-13/2 + sqrt(5)/2, -13/2 - sqrt(5)/2} |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-quad-037 (quadratic equation) - sim-rule-confused

**Problem:** Solve for x (give all real solutions): x**2 - 64 = 0

**Expected:** `8, -8`  |  **Model answer:** `-sqrt(67), sqrt(67)`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 = 67` | **arithmetic_slip** - solutions changed from {-8, 8} to {sqrt(67), -sqrt(67)} |
| final answer | `-sqrt(67), sqrt(67)` | unreadable |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-quad-039 (quadratic equation) - sim-rule-confused

**Problem:** Solve for x (give all real solutions): x**2 - 15*x + 56 = 0

**Expected:** `7, 8`  |  **Model answer:** `5, 8`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 - 15*x = -56` | ok |
| final answer | `5, 8` | **unjustified_leap** - final answer '5, 8' does not follow from last step 'x**2 - 15*x = -56' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-frac-021 (fraction arithmetic) - sim-rule-confused

**Problem:** Compute exactly: (8/2 + 6/8)*6

**Expected:** `57/2`  |  **Model answer:** `29`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `(76/16)*6` | ok |
| 2 | `29` | **arithmetic_slip** - '29' does not follow from '(76/16)*6': got 29, expected 57/2 |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-expand-012 (polynomial simplification) - sim-rule-confused

**Problem:** Expand and simplify: (x - 7)**2 - (x + 9)**2

**Expected:** `-32*x - 32`  |  **Model answer:** `-32*x - 33`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `(x**2 - 14*x + 49) - (x**2 + 18*x + 81)` | ok |
| final answer | `-32*x - 33` | **unjustified_leap** - final answer '-32*x - 33' does not follow from last step '(x**2 - 14*x + 49) - (x**2 + 18*x + 81)' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-expand-019 (polynomial simplification) - sim-rule-confused

**Problem:** Expand and simplify: (x - 1)**2 - (x + 9)**2

**Expected:** `-20*x - 80`  |  **Model answer:** `-20*x - 81`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `(x**2 - 2*x + 1) - (x**2 + 18*x + 81)` | ok |
| final answer | `-20*x - 81` | **unjustified_leap** - final answer '-20*x - 81' does not follow from last step '(x**2 - 2*x + 1) - (x**2 + 18*x + 81)' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-expand-024 (polynomial simplification) - sim-rule-confused

**Problem:** Expand and simplify: (x - 1)**2 - (x + 7)**2

**Expected:** `-16*x - 48`  |  **Model answer:** `-16*x - 47`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `(x**2 - 2*x + 1) - (x**2 + 14*x + 49)` | ok |
| final answer | `-16*x - 47` | **unjustified_leap** - final answer '-16*x - 47' does not follow from last step '(x**2 - 2*x + 1) - (x**2 + 14*x + 49)' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-expand-031 (polynomial simplification) - sim-rule-confused

**Problem:** Expand and simplify: (x - 5)**2 - (x - 1)**2

**Expected:** `24 - 8*x`  |  **Model answer:** `23 - 8*x`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `(x**2 - 10*x + 25) - (x**2 - 2*x + 1)` | ok |
| final answer | `23 - 8*x` | **unjustified_leap** - final answer '23 - 8*x' does not follow from last step '(x**2 - 10*x + 25) - (x**2 - 2*x + 1)' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### calc-prod-000 (product rule) - sim-rule-confused

**Problem:** Differentiate with respect to x: f(x) = x**6*cos(x)

**Expected:** `-x**6*sin(x) + 6*x**5*cos(x)`  |  **Model answer:** `x**6*sin(x) + 6*x**5*cos(x)`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `Derivative(x**6, x)*cos(x) - x**6*Derivative(cos(x), x)` | **invalid_algebra** - 'Derivative(x**6, x)*cos(x) - x**6*Derivative(cos(x), x)' does not follow from 'Derivative(x**6*cos(x), x)': got x**5*(x*sin(x) + 6*cos(x)), expected x**6*cos(x), or x**5*(-x*sin(x) + 6*cos(x)) after differentiating |
| 2 | `x**6*sin(x) + 6*x**5*cos(x)` | carries earlier error |

> Reasoning first breaks at step 1: **invalid_algebra**.

### calc-prod-004 (product rule) - sim-rule-confused

**Problem:** Differentiate with respect to x: f(x) = x**2*log(x)

**Expected:** `2*x*log(x) + x`  |  **Model answer:** `2*x*log(x) + x`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `Derivative(x**2, x)*log(x) + x**2*Derivative(log(x), x)` | ok |
| 2 | `2*x*1/x` | **misapplied_rule** - '2*x*1/x' does not follow from 'Derivative(x**2, x)*log(x) + x**2*Derivative(log(x), x)': got 2, expected x*(2*log(x) + 1) |
| 3 | `2` | carries earlier error |
| final answer | `2*x*log(x) + x` | **unjustified_leap** - final answer '2*x*log(x) + x' does not follow from last step '2' |

> Reasoning first breaks at step 2: **misapplied_rule**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### calc-prod-008 (product rule) - sim-rule-confused

**Problem:** Differentiate with respect to x: f(x) = x**3*exp(x)

**Expected:** `x**3*exp(x) + 3*x**2*exp(x)`  |  **Model answer:** `3*x**2*exp(x)`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `Derivative(x**3, x)*exp(x) + x**3*Derivative(exp(x), x)` | ok |
| 2 | `3*x**2*exp(x)` | **misapplied_rule** - '3*x**2*exp(x)' does not follow from 'Derivative(x**3, x)*exp(x) + x**3*Derivative(exp(x), x)': got 3*x**2*exp(x), expected x**2*(x + 3)*exp(x) |

> Reasoning first breaks at step 2: **misapplied_rule**.

### calc-prod-009 (product rule) - sim-rule-confused

**Problem:** Differentiate with respect to x: f(x) = x**4*cos(x)

**Expected:** `-x**4*sin(x) + 4*x**3*cos(x)`  |  **Model answer:** `-4*x**3*sin(x)`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `Derivative(x**4, x)*cos(x) + x**4*Derivative(cos(x), x)` | ok |
| 2 | `4*x**3*-sin(x)` | **misapplied_rule** - '4*x**3*-sin(x)' does not follow from 'Derivative(x**4, x)*cos(x) + x**4*Derivative(cos(x), x)': got -4*x**3*sin(x), expected x**3*(-x*sin(x) + 4*cos(x)) |
| 3 | `-4*x**3*sin(x)` | carries earlier error |

> Reasoning first breaks at step 2: **misapplied_rule**.
