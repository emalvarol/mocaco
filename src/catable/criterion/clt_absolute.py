"""CLT absolute convergence criterion.

Predefined structure for auto-discovery:

* ``CltAbsoluteParams`` — Pydantic model for criterion parameters.
* ``compute(df, it_col, target_col, params) -> pl.DataFrame`` — core logic.

The convergence table returned has columns ``it | criterion | converged``.

Theory
------
For i.i.d. Monte Carlo output the CLT gives
``mean_n ± z_{1-alpha/2} * sigma / sqrt(n)`` as an asymptotic
``1-alpha`` confidence interval. ``half_width = z * sigma / sqrt(n)``.

Convergence is reported per iteration ``n`` as

    converged_n = half_width_n <= threshold

``epsilon`` is kept as an alias for ``threshold`` for backwards
compatibility; when both are provided ``threshold`` wins. ``alpha``
sets the confidence level (default ``0.05`` → ``z≈1.96``).
"""

from __future__ import annotations

import math

import polars as pl
from pydantic import BaseModel, ConfigDict, Field
from scipy.stats import norm


class CltAbsoluteParams(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    epsilon: float = Field(default=0.1, gt=0, description="legacy alias for threshold")
    alpha: float = Field(default=0.05, gt=0, lt=1, description="significance level")
    threshold: float = Field(default=1.0, gt=0, description="absolute half-width threshold")


def compute(
    df: pl.DataFrame,
    it_col: str,
    target_col: str,
    params: CltAbsoluteParams,
) -> pl.DataFrame:
    """Compute CLT absolute convergence per iteration.

    Args:
        df: Polars DataFrame sorted or unsorted; will be sorted by ``it_col``.
        it_col: iteration column name.
        target_col: value column name.
        params: validated criterion parameters.

    Returns:
        Polars DataFrame with columns ``it``, ``criterion``, ``converged``.
    """
    # sort by iteration to ensure expanding window is correct
    sorted_df = df.sort(it_col)
    it_vals: list[int | float] = sorted_df[it_col].to_list()
    values: list[float] = sorted_df[target_col].to_list()

    # z for two-sided interval
    z = float(norm.ppf(1.0 - params.alpha / 2.0))
    # threshold takes precedence; epsilon is alias
    tol = float(params.threshold)

    converged: list[bool] = []
    # expanding window: compute mean/std/half_width for each prefix
    # O(n^2) is fine for n=50 and keeps code easy to read/collaborate
    for n in range(1, len(values) + 1):
        window = values[:n]
        if n < 2:
            converged.append(False)
            continue
        mean = sum(window) / n
        # sample std ddof=1
        var = sum((x - mean) ** 2 for x in window) / (n - 1)
        std = math.sqrt(var) if var > 0 else 0.0
        half_width = z * std / math.sqrt(n) if std != 0 else 0.0
        converged.append(half_width <= tol)

    return pl.DataFrame(
        {
            "it": it_vals,
            "criterion": ["clt_absolute"] * len(it_vals),
            "converged": converged,
        }
    )
