"""Bootstrap statistics for comparing models on the same problem set."""
from __future__ import annotations

import numpy as np


def bootstrap_ci(values, n_boot: int = 5000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float, float]:
    """Mean and percentile bootstrap (1 - alpha) confidence interval."""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, v.size, size=(n_boot, v.size))].mean(axis=1)
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return float(v.mean()), float(lo), float(hi)


def paired_bootstrap(a, b, n_boot: int = 5000, alpha: float = 0.05, seed: int = 0) -> dict:
    """Compare two models scored on the *same* problems (paired by index).

    Resamples problems (not individual scores) so per-problem difficulty is shared.
    Returns the mean difference a - b, its CI, and a two-sided bootstrap p-value.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    assert a.shape == b.shape, "paired bootstrap needs both models scored on the same problems"
    d = a - b
    rng = np.random.default_rng(seed)
    boots = d[rng.integers(0, d.size, size=(n_boot, d.size))].mean(axis=1)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    p = 2 * min((boots <= 0).mean(), (boots >= 0).mean())
    return {"diff": float(d.mean()), "ci_low": float(lo), "ci_high": float(hi), "p_value": float(min(1.0, p)),
            "significant": bool(lo > 0 or hi < 0)}
