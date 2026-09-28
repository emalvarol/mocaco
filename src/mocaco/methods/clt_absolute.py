from __future__ import annotations

from dataclasses import dataclass, field

import polars as pl
from scipy.stats import norm

from ..protocols import SampleFrame
from ..result import ConvergenceResult


# 1. Criterion input parameters
@dataclass(frozen=True)
class CLTAbsoluteParams:
    threshold: float = field(
        metadata={
            "description": (
                "Maximum accepted absolute Monte Carlo error."
            )
        }
    )

    confidence_level: float = field(
        default=0.95,
        metadata={
            "description": (
                "Confidence level used for the CLT margin of error."
            )
        },
    )

    stb_window: int = field(
        default=30,
        metadata={
            "description": (
                "Minimum number of consecutive iterations "
                "meeting the threshold."
            )
        },
    )

    def __post_init__(self) -> None:
        if self.threshold <= 0:
            raise ValueError(
                "threshold must be greater than zero."
            )

        if not 0 < self.confidence_level < 1:
            raise ValueError(
                "confidence_level must be between 0 and 1."
            )

        if self.stb_window < 1:
            raise ValueError(
                "stb_window must be at least 1."
            )

        if not isinstance(self.stb_window, int):
            raise TypeError(
                "stb_window must be an integer."
            )

# 2. Criterion logic (calculous)
class CLTAbsoluteCriterion:
    name = "clt_absolute"

    description = (
        "Central Limit Theorem based convergence criterion "
        "using an absolute Monte Carlo error threshold."
    )

    params_type = CLTAbsoluteParams

    def run(
        self,
        samples: SampleFrame,
        params: CLTAbsoluteParams,
    ) -> ConvergenceResult:

        df = samples.df.sort(samples.it_col)

        target = pl.col(samples.target_col).cast(pl.Float64)

        n = target.cum_count()

        cum_sum = target.cum_sum()
        cum_sum_sq = (target**2).cum_sum()

        # Sample variance:
        #
        # s²_n =
        #     [sum(x²) - sum(x)² / n] / (n - 1)
        #
        cum_var = (
            (
                cum_sum_sq
                - (cum_sum**2) / n
            )
            / (n - 1)
        )

        cum_std = (
            pl.when(n > 1)
            .then(
                cum_var
                .clip(lower_bound=0.0)
                .sqrt()
            )
            .otherwise(0.0)
        )

        sem = cum_std / n.sqrt()

        z_score = float(
            norm.ppf(
                1.0 - (1.0 - params.confidence_level) / 2.0
            )
        )

        abs_error = sem * z_score

        meets_threshold = (
            abs_error <= params.threshold
        )

        is_converged = (
            meets_threshold
            .cast(pl.Int32)
            .rolling_sum(
                window_size=params.stb_window
            )
            .fill_null(0)
            == params.stb_window
        )

        result_df = df.with_columns(
            [
                n.alias("cum_n"),
                (cum_sum / n).alias("cum_mean"),
                cum_std.alias("cum_std"),
                sem.alias("sem"),
                abs_error.alias("abs_error"),
                meets_threshold.alias("meets_threshold"),
                is_converged.alias("is_converged"),
            ]
        )

        final = result_df.tail(1).to_dicts()[0]

        return ConvergenceResult(
            method=self.name,
            data=result_df,
            converged=bool(final["is_converged"]),
            estimate=(
                float(final["cum_mean"])
                if final["cum_mean"] is not None
                else None
            ),
            error=(
                float(final["abs_error"])
                if final["abs_error"] is not None
                else None
            ),
            n=int(final["cum_n"]),
            diagnostics={
                "threshold": params.threshold,
                "confidence_level": params.confidence_level,
                "stb_window": params.stb_window,
                "z_score": z_score,
                "it_col": samples.it_col,
                "target_col": samples.target_col,
            },
        )

# 3. Criterion user API
def clt_absolute(
    samples: SampleFrame,
    *,
    threshold: float,
    confidence_level: float = 0.95,
    stb_window: int = 30,
) -> ConvergenceResult:
    """Run the CLT absolute-error convergence criterion."""
    # Deferred import to avoid circular dependency
    from ..api import convergence

    return convergence(
        samples,
        method="clt_absolute",
        threshold=threshold,
        confidence_level=confidence_level,
        stb_window=stb_window,
    )
