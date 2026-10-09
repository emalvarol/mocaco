"""Custom criterion method."""

import polars as pl
from pydantic import BaseModel, Field

import mocaco as mcc
from mocaco.registry import registry
from mocaco.result import ConvergenceResult


# 1. Define input parameters via Pydantic
class SimpleMeanParams(BaseModel):
    target_mean: float = Field(..., description="Target value to reach.")
    tolerance: float = Field(0.01, description="Absolute tolerance.")


# 2. Create and register the criterion
@registry.register()
class SimpleMeanCriterion:
    name = "simple_mean"
    supports_eval_frequency = True
    description = "Checks if the cumulative mean is within a tolerance."
    params_type = SimpleMeanParams
    assumptions = ("Finite variance",)
    limitations = ("Basic example logic only.",)
    result_interpretation = "Converges when mean is near target."
    example_usage = "..."
    references = ()

    def run(self, samples, params: SimpleMeanParams) -> ConvergenceResult:
        # Simple logic: calculate cumulative mean of the target column
        target = pl.col(samples.target_col).cast(pl.Float64)
        agg_df = samples.df.select([pl.len().alias("n"), target.mean().alias("mean")])

        final = agg_df.row(0, named=True)
        n = final["n"]
        mean = final["mean"]

        error = abs(mean - params.target_mean) if mean is not None else float("inf")
        is_converged = error <= params.tolerance

        # Build diagnostic output
        final_df = pl.DataFrame(
            {"n": [n], "mean": [mean], "error": [error], "is_converged": [is_converged]}
        )

        return ConvergenceResult(
            method=self.name,
            n=int(n),
            n_col="n",
            estimate=float(mean) if mean is not None else None,
            estimate_col="mean",
            error=float(error),
            error_col="error",
            is_converged=is_converged,
            is_converged_col="is_converged",
            data=final_df,
        )


# 3. Test the custom criterion
df = pl.DataFrame({"it": range(1, 101), "val": [5.0] * 100})
samples = mcc.samples(df, it_col="it", target_col="val")

# Because we registered it, it is now available via the API
result = mcc.convergence.simple_mean(samples, target_mean=5.0, tolerance=0.1)  # type:ignore
print(f"Custom criterion converged: {result.is_converged}")
