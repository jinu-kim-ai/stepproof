# Error report: sim-hasty

118 attempts with at least one invalid step (showing up to 25).

### alg-lin1-001 (linear equation) - sim-hasty

**Problem:** Solve for x: 8*x - 17 = 23

**Expected:** `5`  |  **Model answer:** `21/4`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `8*x = 42` | **arithmetic_slip** - solutions changed from {5} to {21/4} |
| 2 | `x = 21/4` | carries earlier error |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-lin1-006 (linear equation) - sim-hasty

**Problem:** Solve for x: 8*x - 16 = -32

**Expected:** `-2`  |  **Model answer:** `-2`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `8*x = -16` | ok |
| 2 | `x = -4` | **arithmetic_slip** - solutions changed from {-2} to {-4} |
| final answer | `-2` | **unjustified_leap** - final answer '-2' does not follow from last step 'x = -4' |

> Reasoning first breaks at step 2: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-lin1-011 (linear equation) - sim-hasty

**Problem:** Solve for x: 2*x + 17 = 23

**Expected:** `3`  |  **Model answer:** `4`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `2*x = 6` | ok |
| final answer | `4` | **unjustified_leap** - final answer '4' does not follow from last step '2*x = 6' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-lin1-017 (linear equation) - sim-hasty

**Problem:** Solve for x: 3*x + 16 = 25

**Expected:** `3`  |  **Model answer:** `11/3`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `3*x = 11` | **arithmetic_slip** - solutions changed from {3} to {11/3} |
| 2 | `x = 11/3` | carries earlier error |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-lin1-021 (linear equation) - sim-hasty

**Problem:** Solve for x: 5*x + 14 = 14

**Expected:** `0`  |  **Model answer:** `1/5`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `5*x = 1` | **arithmetic_slip** - solutions changed from {0} to {1/5} |
| 2 | `x = 1/5` | carries earlier error |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-lin1-028 (linear equation) - sim-hasty

**Problem:** Solve for x: 9*x + 18 = -36

**Expected:** `-6`  |  **Model answer:** `-8`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `9*x = -54` | ok |
| 2 | `x = -8` | **arithmetic_slip** - solutions changed from {-6} to {-8} |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-lin1-033 (linear equation) - sim-hasty

**Problem:** Solve for x: 10*x + 1 = 31

**Expected:** `3`  |  **Model answer:** `2`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `10*x = 30` | ok |
| 2 | `x = 2` | **arithmetic_slip** - solutions changed from {3} to {2} |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-lin1-034 (linear equation) - sim-hasty

**Problem:** Solve for x: 7*x + 11 = 39

**Expected:** `4`  |  **Model answer:** `1`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `7*x = 28` | ok |
| 2 | `x = 1` | **arithmetic_slip** - solutions changed from {4} to {1} |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-lin1-036 (linear equation) - sim-hasty

**Problem:** Solve for x: 3*x - 15 = 18

**Expected:** `11`  |  **Model answer:** `12`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `3*x = 33` | ok |
| 2 | `x = 12` | **arithmetic_slip** - solutions changed from {11} to {12} |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-lin2-006 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 6*x + 15 = 26 - 5*x

**Expected:** `1`  |  **Model answer:** `1`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `11*x = 11` | ok |
| 2 | `x = -1` | **arithmetic_slip** - solutions changed from {1} to {-1} |
| final answer | `1` | **unjustified_leap** - final answer '1' does not follow from last step 'x = -1' |

> Reasoning first breaks at step 2: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-lin2-015 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 8*x + 5 = 3*x + 5

**Expected:** `0`  |  **Model answer:** `0`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `5*x = -3` | **arithmetic_slip** - solutions changed from {0} to {-3/5} |
| 2 | `x = -3/5` | carries earlier error |
| final answer | `0` | **unjustified_leap** - final answer '0' does not follow from last step 'x = -3/5' |

> Reasoning first breaks at step 1: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-lin2-018 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 9*x + 1 = -4*x - 116

**Expected:** `-9`  |  **Model answer:** `-120/13`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `13*x = -120` | **arithmetic_slip** - solutions changed from {-9} to {-120/13} |
| 2 | `x = -120/13` | carries earlier error |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-lin2-019 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 11*x - 20 = -8*x - 191

**Expected:** `-9`  |  **Model answer:** `-10`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `19*x = -171` | ok |
| 2 | `x = -10` | **arithmetic_slip** - solutions changed from {-9} to {-10} |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-lin2-027 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 6*x - 19 = 21 - 4*x

**Expected:** `4`  |  **Model answer:** `3`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `10*x = 40` | ok |
| 2 | `x = 3` | **arithmetic_slip** - solutions changed from {4} to {3} |

> Reasoning first breaks at step 2: **arithmetic_slip**.

### alg-lin2-028 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 5*x - 11 = 7*x - 9

**Expected:** `-1`  |  **Model answer:** `1`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `-2*x = 2` | ok |
| final answer | `1` | **unjustified_leap** - final answer '1' does not follow from last step '-2*x = 2' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-lin2-031 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 10*x + 2 = 2*x - 54

**Expected:** `-7`  |  **Model answer:** `-8`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `8*x = -56` | ok |
| final answer | `-8` | **unjustified_leap** - final answer '-8' does not follow from last step '8*x = -56' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-lin2-033 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 7*x - 8 = 55 - 2*x

**Expected:** `7`  |  **Model answer:** `20/3`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `9*x = 60` | **arithmetic_slip** - solutions changed from {7} to {20/3} |
| 2 | `x = 20/3` | carries earlier error |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-lin2-038 (linear equation (both sides)) - sim-hasty

**Problem:** Solve for x: 7*x + 2 = 5*x + 24

**Expected:** `11`  |  **Model answer:** `11`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `2*x = 22` | ok |
| 2 | `x = 10` | **arithmetic_slip** - solutions changed from {11} to {10} |
| final answer | `11` | **unjustified_leap** - final answer '11' does not follow from last step 'x = 10' |

> Reasoning first breaks at step 2: **arithmetic_slip**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).

### alg-quad-008 (quadratic equation) - sim-hasty

**Problem:** Solve for x (give all real solutions): x**2 + 6*x - 7 = 0

**Expected:** `1, -7`  |  **Model answer:** `1`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 + 6*x = 7` | ok |
| 2 | `x - 1 = 0` | **invalid_algebra** - solutions changed from {-7, 1} to {1} |
| 3 | `x = 1` | carries earlier error |

> Reasoning first breaks at step 2: **invalid_algebra**.

### alg-quad-009 (quadratic equation) - sim-hasty

**Problem:** Solve for x (give all real solutions): x**2 - 8*x + 15 = 0

**Expected:** `3, 5`  |  **Model answer:** `4, 5`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 - 8*x = -15` | ok |
| final answer | `4, 5` | **unjustified_leap** - final answer '4, 5' does not follow from last step 'x**2 - 8*x = -15' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-quad-010 (quadratic equation) - sim-hasty

**Problem:** Solve for x (give all real solutions): x**2 + 4*x - 21 = 0

**Expected:** `3, -7`  |  **Model answer:** `-7, -3`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 + 4*x = 21` | ok |
| 2 | `(x + 3)*(x + 7) = 0` | **invalid_algebra** - solutions changed from {-7, 3} to {-7, -3} |

> Reasoning first breaks at step 2: **invalid_algebra**.

### alg-quad-012 (quadratic equation) - sim-hasty

**Problem:** Solve for x (give all real solutions): x**2 + 14*x + 45 = 0

**Expected:** `-9, -5`  |  **Model answer:** `-8, -6`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 + 14*x = -48` | **arithmetic_slip** - solutions changed from {-5, -9} to {-8, -6} |

> Reasoning first breaks at step 1: **arithmetic_slip**.

### alg-quad-016 (quadratic equation) - sim-hasty

**Problem:** Solve for x (give all real solutions): x**2 - 3*x - 40 = 0

**Expected:** `8, -5`  |  **Model answer:** `-8, -5`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 - 3*x = 40` | ok |
| 2 | `(x + 5)*(x + 8) = 0` | **invalid_algebra** - solutions changed from {8, -5} to {-8, -5} |

> Reasoning first breaks at step 2: **invalid_algebra**.

### alg-quad-017 (quadratic equation) - sim-hasty

**Problem:** Solve for x (give all real solutions): x**2 + 15*x + 54 = 0

**Expected:** `-9, -6`  |  **Model answer:** `-8, -6`  |  **Answer correct:** no

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 + 15*x = -54` | ok |
| final answer | `-8, -6` | **unjustified_leap** - final answer '-8, -6' does not follow from last step 'x**2 + 15*x = -54' |

> Reasoning first breaks at the final answer: **unjustified_leap**.

### alg-quad-018 (quadratic equation) - sim-hasty

**Problem:** Solve for x (give all real solutions): x**2 - 2*x - 35 = 0

**Expected:** `7, -5`  |  **Model answer:** `7, -5`  |  **Answer correct:** yes

| Step | Content | Verdict |
|---|---|---|
| 1 | `x**2 - 2*x = 35` | ok |
| 2 | `x - 7 = 0` | **invalid_algebra** - solutions changed from {-5, 7} to {7} |
| 3 | `x = 7` | carries earlier error |
| final answer | `7, -5` | **unjustified_leap** - final answer '7, -5' does not follow from last step 'x = 7' |

> Reasoning first breaks at step 2: **invalid_algebra**.
> Final answer is correct, but the written reasoning does not support it (lucky guess).
