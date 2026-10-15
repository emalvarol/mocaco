"""Multivariate CLT based convergence criterion using a relative confidence-region volume tolerance (Vats et al., 2019)."""

# Mandatory basic modules
from __future__ import annotations

import math
import warnings
from typing import TYPE_CHECKING

# Basic modules used to build the criterion (According contributor needs)
import numpy as np
import polars as pl
from pydantic import BaseModel, Field
from scipy import stats

# Modules needed from mocaco
from mocaco.registry import registry
from mocaco.result import ConvergenceResult, GroupedConvergenceResult

if TYPE_CHECKING:
    from mocaco.protocols import SampleFrame


# 1. Criterion input parameters
class InputParams(BaseModel):
    alpha: float = Field(
        default=0.05,
        gt=0,
        lt=1,
        description=(
            "Significance level of the Hotelling F-based confidence region that builds "
            "the left-hand side of the rule (the confidence-region radius, i.e. the error). "
            "The confidence level is 1 - alpha."
        ),
    )

    epsilon: float = Field(
        default=0.05,
        gt=0,
        description=(
            "Relative tolerance applied to the natural scale of the target distribution, "
            "det(cov)^(1/(2p)). It defines the threshold rhs = epsilon * det(cov)^(1/(2p)); "
            "convergence requires the confidence-region radius (error) to fall below it."
        ),
    )

    eval_frequency: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Step interval (in iterations) between convergence checkpoints. "
            "If None, the criterion is evaluated once at the final sample."
        ),
    )

    warm_up_period: int = Field(
        default=100,
        ge=100,
        description=(
            "Warm-up sample size (n*) before which convergence is never declared and at "
            "which the first checkpoint is taken."
        ),
    )


# 2. Criterion logic (calculous)
def _vats_components(
    matrix: np.ndarray,
    alpha: float,
    epsilon: float,
) -> tuple[float, float, float, float]:
    """
    Compute the Vats et al. (2019) relative fixed-volume components at a given sample size.

    Returns ``(estimate, error, threshold, residual)`` where:

    * ``estimate`` is the natural scale of the target, ``det(cov)^(1/(2p))``;
    * ``error`` is the confidence-region radius, ``Vol(C_alpha(n))^(1/p) + n^-1``;
    * ``threshold`` is the relative tolerance, ``epsilon * det(cov)^(1/(2p))``;
    * ``residual`` is ``max(0, error - threshold)``. A value of ``0.0`` means the stopping
      rule is satisfied at this checkpoint (``error <= threshold``).

    Degenerate inputs (fewer than two varying columns, ``n <= p``, or a non-positive
    determinant of the sample covariance) return all-zero components, which count as
    convergence at that checkpoint.
    """
    n = matrix.shape[0]
    if n <= 1:
        return (0.0, 0.0, 0.0, 0.0)

    col_var = np.var(matrix, axis=0, ddof=1)
    active = col_var > 0
    p_eff = int(active.sum())

    if p_eff < 2 or n <= p_eff:
        return (0.0, 0.0, 0.0, 0.0)

    sub = matrix[:, active].astype(np.float64)
    cov = np.cov(sub, rowvar=False, ddof=1)
    det = float(np.linalg.det(cov))

    if det <= 0:
        return (0.0, 0.0, 0.0, 0.0)

    unit_ball_vol = math.pi ** (p_eff / 2) / math.gamma(p_eff / 2 + 1)
    c_n = (p_eff * (n - 1) / (n - p_eff)) * stats.f.ppf(1 - alpha, p_eff, n - p_eff)

    vol = unit_ball_vol * (c_n / n) ** (p_eff / 2) * (det**0.5)
    estimate = det ** (1 / (2 * p_eff))
    error = vol ** (1 / p_eff) + 1 / n
    threshold = epsilon * estimate
    residual = max(0.0, error - threshold)

    return (float(estimate), float(error), float(threshold), float(residual))


@registry.register()
class CLTMultivariateRelativeCriterion:
    name = "clt_multi_rel"

    description = (
        "Multivariate Central Limit Theorem based convergence criterion using a "
        "relative confidence-region volume tolerance (Vats et al., 2019)."
    )

    dimensionality = "multivariate"

    params_type = InputParams

    assumptions = (
        "Samples are independent and identically distributed (i.i.d.).",
        "The vector target quantity has finite second moments and a positive-definite covariance matrix.",
        "The sample size reaches the warm-up period (default 100) for the multivariate CLT to hold.",
        "At least two target columns are provided and they are not perfectly collinear.",
    )

    limitations = (
        "This is a probabilistic stopping criterion, not a proof of convergence.",
        "Requires n > p effective dimensions for the sample covariance to be invertible.",
        "When the covariance is degenerate (fewer than two varying columns, n <= p, or a "
        "non-positive determinant) the error, threshold and residual are reported as 0 and "
        "count as convergence at that checkpoint (still gated by the warm-up period).",
        "The threshold (epsilon * det^(1/(2p))) depends on n; a single final value is stored "
        "in diagnostics, so the module-level residual evolution is asymptotic (exact at the "
        "last checkpoint).",
        "No scalar target estimate is produced; estimate is the natural scale det^(1/(2p)) and "
        "the estimate +/- error band from plot.evolution is not physically meaningful here.",
        "Does not detect systematic bias or non-stationarity in the sampling process.",
    )

    result_interpretation = (
        "is_converged is True when, at the last checkpoint with n >= warm_up_period, the error "
        "(confidence-region radius) is at or below the threshold (epsilon * natural scale), i.e. "
        "residual == 0. estimate is the natural scale det^(1/(2p)) of the target. error is the "
        "confidence-region radius. threshold is the relative tolerance. residual_error is "
        "max(0, error - threshold) at the final checkpoint. n is the final checkpoint iteration. "
        "data holds the estimate, error, non_conv_count and is_converged evolution across checkpoints."
    )

    example_usage = """\
import polars as pl
import mocaco as mcc

df = pl.DataFrame({
    "it": list(range(200)) * 1,
    "a": [float(i % 7) for i in range(200)],
    "b": [float((i * 2) % 11) for i in range(200)],
})
samples = mcc.samples(df, it_col="it", target_col=["a", "b"])
result = mcc.convergence.clt_multi_rel(samples)
print(result.is_converged)"""

    references = (
        "Vats, D., Flegal, J. M., & Jones, G. L. (2019). Multivariate output analysis for "
        "Markov chain Monte Carlo. Biometrika, 106(2), 321-337. "
        "https://doi.org/10.1093/biomet/asz002",
    )

    def run(
        self,
        samples: SampleFrame,
        params: InputParams,
    ) -> ConvergenceResult | GroupedConvergenceResult:

        alpha = params.alpha
        epsilon = params.epsilon
        warm_up = params.warm_up_period
        target_cols = list(samples.target_cols)
        p_targets = len(target_cols)
        it_col = samples.it_col
        assert it_col is not None  # guaranteed by SampleFrame normalization

        def _warning_result(n_samples: int, message: str) -> ConvergenceResult:
            return ConvergenceResult(
                method=self.name,
                n=n_samples,
                n_col="n",
                estimate=None,
                estimate_col="estimate",
                error=None,
                error_col="error",
                is_converged=False,
                is_converged_col="is_converged",
                data=pl.DataFrame(
                    schema={
                        "n": pl.Int64(),
                        "estimate": pl.Float64(),
                        "error": pl.Float64(),
                        "non_conv_count": pl.Int64(),
                        "is_converged": pl.Boolean(),
                    }
                ),
                diagnostics={
                    "threshold": 0.0,
                    "alpha": alpha,
                    "epsilon": epsilon,
                    "n_targets": p_targets,
                    "warm_up_period": warm_up,
                    "eval_frequency": params.eval_frequency,
                    "warning": message,
                },
            )

        def _evaluate_partition(df: pl.DataFrame) -> ConvergenceResult:
            n_samples = df.height

            df_sorted = df.sort(it_col)
            g_it: np.ndarray = df_sorted.get_column(it_col).to_numpy()
            g_mat: np.ndarray = (
                df_sorted.select(target_cols).to_numpy().astype(np.float64, copy=False)
            )
            max_it = int(np.max(g_it))

            freq = params.eval_frequency
            if freq is None:
                eval_steps = [max_it]
            else:
                start = min(warm_up, max_it)
                eval_steps = list(range(start, max_it + 1, freq))
                if max_it not in eval_steps:
                    eval_steps.append(max_it)

            rows: list[dict[str, float | int]] = []
            for step in eval_steps:
                k = int(np.searchsorted(g_it, step, side="right"))
                if k <= 1:
                    continue
                estimate, error, threshold, residual = _vats_components(g_mat[:k], alpha, epsilon)
                rows.append(
                    {
                        "n": step,
                        "estimate": estimate,
                        "error": error,
                        "threshold": threshold,
                        "residual": residual,
                        "non_conv_count": int(residual > 0),
                    }
                )

            if not rows:
                return _warning_result(n_samples, "No checkpoint produced a valid residual.")

            res_df = pl.DataFrame(rows)
            res_df = res_df.with_columns(
                ((pl.col("residual") == 0.0) & (pl.col("n") >= warm_up)).alias("is_converged")
            )

            if max_it < warm_up:
                warnings.warn(
                    f"Warm-up period not reached: maximum sample size n={max_it} is below "
                    f"warm_up_period={warm_up}. The result is forced to not converged.",
                    UserWarning,
                    stacklevel=2,
                )
                res_df = res_df.with_columns(pl.lit(False).alias("is_converged"))

            res_df = res_df.select(["n", "estimate", "error", "non_conv_count", "is_converged"])

            final = res_df.row(-1, named=True)
            n_final = int(final["n"])
            estimate_final = float(final["estimate"])
            error_final = float(final["error"])
            threshold_final = float(rows[-1]["threshold"])
            residual_final = float(rows[-1]["residual"])
            is_converged = bool(final["is_converged"])

            return ConvergenceResult(
                method=self.name,
                n=n_final,
                n_col="n",
                estimate=estimate_final,
                estimate_col="estimate",
                error=error_final,
                error_col="error",
                is_converged=is_converged,
                is_converged_col="is_converged",
                data=res_df,
                residual_error=residual_final,
                diagnostics={
                    "threshold": threshold_final,
                    "alpha": alpha,
                    "epsilon": epsilon,
                    "n_targets": p_targets,
                    "warm_up_period": warm_up,
                    "eval_frequency": params.eval_frequency,
                    "n_evaluations": len(res_df),
                },
            )

        # Route single DataFrame or partitioned DataFrames based on group_cols
        if samples.group_cols:
            results = {}
            partitions = samples.df.partition_by(samples.group_cols, as_dict=True)
            for group_vals, group_df in partitions.items():
                if not isinstance(group_vals, tuple):
                    group_vals = (group_vals,)
                named_key = tuple(zip(samples.group_cols, group_vals, strict=True))
                results[named_key] = _evaluate_partition(group_df)
            return GroupedConvergenceResult(results)

        return _evaluate_partition(samples.df)
