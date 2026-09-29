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
class CLTAbsoluteParams(BaseModel):
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

# 2. Criterion logic (calculous)
@registry.register()
class CLTAbsoluteCriterion:
    name = "clt_absolute"

    supports_eval_frequency = True

    description = (
        "Central Limit Theorem based convergence criterion "
        "using an absolute Monte Carlo error threshold."
    )

    params_type = CLTAbsoluteParams

    assumptions = [
        "Samples are independent and identically distributed (i.i.d.).",
        "The target quantity has finite variance.",
        "The sample size is sufficiently large for the CLT to provide a normal approximation. The deafult stb_window = 30 aims to support this assumption.",
    ]

    limitations = [
        "This is a probabilistic stopping criterion, not a proof of convergence.",
        "For small sample sizes, the normal approximation may be inaccurate.",
        "Does not detect systematic bias or non-stationarity in the sampling process.",
        "The stability window introduces a lag in detecting convergence.",
    ]

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
result = mcc.convergence.clt_absolute(samples, threshold=0.1)
print(result.is_converged)"""

    references = [
        "https://en.wikipedia.org/wiki/Central_limit_theorem",
    ]

    def run(
        self,
        samples: SampleFrame,
        params: CLTAbsoluteParams,
    ) -> ConvergenceResult:

        target = pl.col(samples.target_col).cast(pl.Float64)
        
        agg_df = samples.df.select([
            pl.len().alias("n"),
            target.mean().alias("mean"),
            target.std().alias("std")
        ])
        
        final = agg_df.row(0, named=True)
        n = final["n"]
        mean = final["mean"]
        std = final["std"] if final["std"] is not None else 0.0

        sem = std / (n ** 0.5) if n > 0 else 0.0
        z_score = float(norm.ppf(1.0 - (1.0 - params.confidence_level) / 2.0))
        abs_error = sem * z_score
        
        is_converged = abs_error <= params.threshold
        
        final_df = pl.DataFrame({
            "n": [n],
            "mean": [mean],
            "std": [std],
            "sem": [sem],
            "abs_error": [abs_error],
            "is_converged": [is_converged],
        })

        return ConvergenceResult(
            method=self.name,
            n=int(n),
            estimate=float(mean) if mean is not None else None,
            error=float(abs_error),
            is_converged=is_converged,
            data=final_df,
            diagnostics={
                "threshold": params.threshold,
                "confidence_level": params.confidence_level,
                "z_score": z_score,
            },
        )
