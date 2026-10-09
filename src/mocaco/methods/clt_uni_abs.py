"""Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold."""

# Mandatory basic modules
from __future__ import annotations

from typing import TYPE_CHECKING

# Basic modules used to build the criterion (According contributor needs)
import polars as pl
from pydantic import BaseModel, Field
from scipy.stats import norm

# Modules needed from mocaco
from mocaco.registry import registry
from mocaco.result import ConvergenceResult

if TYPE_CHECKING:
    from mocaco.protocols import SampleFrame


# 1. Criterion input parameters
class InputParams(BaseModel):
    threshold: float = Field(
        ...,
        gt=0,
        description="Maximum accepted absolute Monte Carlo error.",
    )

    confidence_level: float = Field(
        0.95,
        gt=0,
        lt=1,
        description="Confidence level used for the CLT margin of error.",
    )

    eval_frequency: int | None = Field(
        default=None,
        gt=0,
        description="Step interval for periodic evaluation of convergence history natively in Polars.",
    )


# 2. Criterion logic (calculous)
@registry.register()
class CLTAbsoluteCriterion:
    name = "clt_uni_abs"

    supports_eval_frequency = False

    description = (
        "Central Limit Theorem based convergence criterion "
        "using an absolute Monte Carlo error threshold."
    )

    params_type = InputParams

    assumptions = (
        "Samples are independent and identically distributed (i.i.d.).",
        "The target quantity has finite variance.",
        "The sample size is sufficiently large for the CLT to provide a normal approximation. The deafult stb_window = 30 aims to support this assumption.",
    )

    limitations = (
        "This is a probabilistic stopping criterion, not a proof of convergence.",
        "For small sample sizes, the normal approximation may be inaccurate.",
        "Does not detect systematic bias or non-stationarity in the sampling process.",
        "The stability window introduces a lag in detecting convergence.",
    )

    result_interpretation = (
        "is_converged is True when the CLT-based absolute error has stayed below "
        "the threshold for at least stb_window consecutive iterations. "
        "estimate is the cumulative mean at the final sample. "
        "error is the CLT-based absolute error (z_score * SEM) at the final sample. "
        "n is the total number of samples evaluated."
    )

    example_usage = """\
import polars as pl
import mocaco as mcc

df = pl.DataFrame({"it": range(100), "value": [1.0] * 100})
samples = mcc.samples(df, it_col="it", target_col="value")
result = mcc.convergence.clt_uni_abs(samples, threshold=0.1)
print(result.is_converged)"""

    references = ("https://en.wikipedia.org/wiki/Central_limit_theorem",)

    def run(
        self,
        samples: SampleFrame,
        params: InputParams,
    ) -> ConvergenceResult:

        target = pl.col(samples.target_col).cast(pl.Float64)
        z_score = float(norm.ppf(1.0 - (1.0 - params.confidence_level) / 2.0))

        # Single-pass evaluation if eval_frequency is not set
        if params.eval_frequency is None or params.eval_frequency == 1:
            agg_df = samples.df.select(
                [pl.len().alias("n"), target.mean().alias("mean"), target.std().alias("std")]
            )

            final = agg_df.row(0, named=True)
            n = final["n"]
            mean = final["mean"]
            std = final["std"] if final["std"] is not None else 0.0

            sem = std / (n**0.5) if n > 0 else 0.0
            abs_error = sem * z_score

            is_converged = abs_error <= params.threshold

            final_df = pl.DataFrame(
                {
                    "n": [n],
                    "mean": [mean],
                    "std": [std],
                    "sem": [sem],
                    "abs_error": [abs_error],
                    "is_converged": [is_converged],
                }
            )

            return ConvergenceResult(
                method=self.name,
                n=int(n),
                n_col="n",
                estimate=float(mean) if mean is not None else None,
                estimate_col="mean",
                error=float(abs_error),
                error_col="abs_error",
                is_converged=is_converged,
                is_converged_col="is_converged",
                data=final_df,
                diagnostics={
                    "threshold": params.threshold,
                    "confidence_level": params.confidence_level,
                    "z_score": z_score,
                },
            )

        # Native vectorization in Polars for eval_frequency
        n_col = pl.int_range(1, pl.len() + 1).alias("n")
        cum_sum = target.cum_sum()
        cum_mean = (cum_sum / n_col).alias("mean")

        cum_sq_sum = (target**2).cum_sum()
        cum_var = (
            pl.when(n_col > 1)
            .then(((cum_sq_sum - n_col * (cum_mean**2)) / (n_col - 1)).clip(lower_bound=0.0))
            .otherwise(0.0)
        )
        cum_std = cum_var.sqrt().alias("std")

        sem = (cum_std / n_col.sqrt()).alias("sem")
        abs_error = (sem * z_score).alias("abs_error")
        is_converged = (abs_error <= params.threshold).alias("is_converged")

        full_df = samples.df.select([n_col, cum_mean, cum_std, sem, abs_error, is_converged])

        freq = params.eval_frequency
        # Downsample to eval_frequency intervals, ensuring the final point is always included
        total_rows = full_df.height
        eval_df = full_df.gather_every(freq, offset=freq - 1)

        if eval_df.is_empty() or eval_df.row(-1, named=True)["n"] != total_rows:
            eval_df = pl.concat([eval_df, full_df.tail(1)])

        final_row = eval_df.row(-1, named=True)
        n_val = int(final_row["n"])
        mean_val = float(final_row["mean"]) if final_row["mean"] is not None else None
        error_val = float(final_row["abs_error"])
        is_conv_val = bool(final_row["is_converged"])

        return ConvergenceResult(
            method=self.name,
            n=n_val,
            n_col="n",
            estimate=mean_val,
            estimate_col="mean",
            error=error_val,
            error_col="abs_error",
            is_converged=is_conv_val,
            is_converged_col="is_converged",
            data=eval_df,
            diagnostics={
                "threshold": params.threshold,
                "confidence_level": params.confidence_level,
                "z_score": z_score,
                "eval_frequency": params.eval_frequency,
                "n_evaluations": len(eval_df),
            },
        )
