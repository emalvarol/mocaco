"""Multivariate CLT based convergence criterion using a relative confidence-region volume tolerance (Vats et al., 2019)."""

# Mandatory basic modules
from __future__ import annotations

import math
import warnings
from typing import TYPE_CHECKING, ClassVar, Literal

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
    threshold: float = Field(
        ...,
        gt=0,
        description=(
            "Relative tolerance of the confidence-region volume, i.e. epsilon "
            "in the relative standard deviation fixed-volume stopping rule."
        ),
    )

    confidence_level: float = Field(
        0.95,
        gt=0,
        lt=1,
        description="Confidence level used to build the multivariate CLT confidence region.",
    )

    eval_frequency: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Step interval (in iterations) between convergence checkpoints. "
            "If None, the criterion is evaluated once at the final sample."
        ),
    )

    first_check_point: int | None = Field(
        default=None,
        gt=0,
        description=(
            "First iteration at which convergence is checked (the paper's n*). "
            "Defaults to eval_frequency, or to the final sample when eval_frequency is None."
        ),
    )


# 2. Criterion logic (calculous)
def _relative_residual(matrix: np.ndarray, alpha: float, epsilon: float) -> float:
    """
    Compute the Vats et al. (2019) relative fixed-volume residual at a given sample size.

    The residual is ``max(0, Vol(C_alpha(n))^(1/p) + n^-1 - epsilon * |Lambda_n|^(1/(2p)))``,
    where ``Vol(C_alpha(n))`` is the volume of the Hotelling confidence ellipsoid. A value of
    ``0.0`` means the stopping rule is satisfied at this checkpoint.
    """
    n = matrix.shape[0]
    if n <= 1:
        return 0.0

    col_var = np.var(matrix, axis=0, ddof=1)
    active = col_var > 0
    p_eff = int(active.sum())

    if p_eff < 2 or n <= p_eff:
        return 0.0

    sub = matrix[:, active].astype(np.float64)
    cov = np.cov(sub, rowvar=False, ddof=1)
    det = np.linalg.det(cov)

    if det <= 0:
        return 0.0

    unit_ball_vol = math.pi ** (p_eff / 2) / math.gamma(p_eff / 2 + 1)
    c_n = (p_eff * (n - 1) / (n - p_eff)) * stats.f.ppf(1 - alpha, p_eff, n - p_eff)

    vol = unit_ball_vol * (c_n / n) ** (p_eff / 2) * (det**0.5)
    lhs = vol ** (1 / p_eff) + 1 / n
    rhs = epsilon * det ** (1 / (2 * p_eff))

    return float(max(0.0, lhs - rhs))


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
        "The sample size is sufficiently large (>30) for the multivariate CLT to hold.",
        "At least two target columns are provided and they are not perfectly collinear.",
    )

    limitations = (
        "This is a probabilistic stopping criterion, not a proof of convergence.",
        "Requires n > p effective dimensions for the sample covariance to be invertible.",
        "When the covariance is degenerate (fewer than two varying columns, n <= p, or a "
        "non-positive determinant) the residual is reported as 0 and counts as convergence "
        "at that checkpoint.",
        "Does not detect systematic bias or non-stationarity in the sampling process.",
        "No scalar estimate is produced; estimate is None and estimate_col is a placeholder. "
    )

    result_interpretation = (
        "is_converged is True when the relative confidence-region volume criterion is "
        "satisfied at the last checkpoint (n > 30 and residual == 0). "
        "error is the residual (already net of the tolerance; 0 means the rule is satisfied) "
        "at the final checkpoint. residual_error equals error because the residual is reported "
        "relative to a zero effective threshold. n is the final checkpoint iteration. "
        "data holds the residual and non_conv_count evolution across checkpoints."
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
result = mcc.convergence.clt_multi_rel(samples, threshold=0.1)
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

        alpha = 1.0 - params.confidence_level
        target_cols = list(samples.target_cols)
        p_targets = len(target_cols)
        it_col = samples.it_col
        assert it_col is not None  # guaranteed by SampleFrame normalization

        def _evaluate_partition(df: pl.DataFrame) -> ConvergenceResult:
            # Assumption
            n_samples = df.height
            if n_samples < 30:
                warnings.warn(
                    f"Sample size n={n_samples} is less than the required minimum of 30 "
                    "for the multivariate Central Limit Theorem to hold.",
                    UserWarning,
                    stacklevel=2,
                )
                return ConvergenceResult(
                    method=self.name,
                    n=n_samples,
                    n_col="n",
                    estimate=None,
                    estimate_col="estimate",
                    error=None,
                    error_col="residual",
                    is_converged=False,
                    is_converged_col="is_converged",
                    data=pl.DataFrame(),
                    diagnostics={
                        "threshold": 0.0,
                        "tolerance": params.threshold,
                        "confidence_level": params.confidence_level,
                        "n_targets": p_targets,
                        "warning": f"Insufficient sample size (n={n_samples} < 30).",
                    },
                )

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
                if params.first_check_point is not None:
                    start = min(max(int(params.first_check_point), 1), max_it)
                    eval_steps = list(range(start, max_it + 1, freq))
                else:
                    eval_steps = list(range(freq, max_it + 1, freq))
                if max_it not in eval_steps:
                    eval_steps.append(max_it)

            rows: list[dict[str, float | int]] = []
            for step in eval_steps:
                k = int(np.searchsorted(g_it, step, side="right"))
                if k <= 1:
                    continue
                residual = _relative_residual(g_mat[:k], alpha, params.threshold)
                rows.append({"n": step, "residual": residual, "non_conv_count": int(residual > 0)})

            if not rows:
                return ConvergenceResult(
                    method=self.name,
                    n=n_samples,
                    n_col="n",
                    estimate=None,
                    estimate_col="estimate",
                    error=None,
                    error_col="residual",
                    is_converged=False,
                    is_converged_col="is_converged",
                    data=pl.DataFrame(),
                    diagnostics={
                        "threshold": 0.0,
                        "tolerance": params.threshold,
                        "confidence_level": params.confidence_level,
                        "n_targets": p_targets,
                        "warning": "No checkpoint produced a valid residual.",
                    },
                )

            res_df = pl.DataFrame(rows)
            met = (pl.col("n") > 30) & (pl.col("residual") == 0.0)
            res_df = res_df.with_columns(met.alias("met"))
            blocks = (~pl.col("met")).cum_sum()
            res_df = res_df.with_columns(
                pl.col("met").cast(pl.Int64).cum_sum().over(blocks).alias("stc_ag")
            ).with_columns((pl.col("stc_ag") >= 1).alias("is_converged"))
            res_df = res_df.select(["n", "residual", "non_conv_count", "is_converged"])

            final = res_df.row(-1, named=True)
            n_final = int(final["n"])
            residual_final = float(final["residual"])
            is_converged = bool(final["is_converged"])

            return ConvergenceResult(
                method=self.name,
                n=n_final,
                n_col="n",
                estimate=None,
                estimate_col="estimate",
                error=residual_final,
                error_col="residual",
                is_converged=is_converged,
                is_converged_col="is_converged",
                data=res_df,
                residual_error=residual_final,
                diagnostics={
                    "threshold": 0.0,
                    "tolerance": params.threshold,
                    "confidence_level": params.confidence_level,
                    "alpha": alpha,
                    "n_targets": p_targets,
                    "eval_frequency": params.eval_frequency,
                    "first_check_point": params.first_check_point,
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
