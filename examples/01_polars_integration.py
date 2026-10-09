"""Integration with polars DataFrame."""

import polars as pl

import mocaco as mcc

# 1. Prepare simulation data
df = pl.DataFrame(
    {"iteration": range(1, 1001), "mc_estimate": [1.0 + (1 / i) for i in range(1, 1001)]}
)

# 2. Freeze into a SampleFrame (validates inputs)
samples = mcc.samples(df, it_col="iteration", target_col="mc_estimate")

# 3. Run a criterion
result = mcc.convergence.clt_absolute(samples, threshold=0.05)

# 4. Extract diagnostics back to Polars for downstream analysis
diagnostics_df = result.to_polars()
print("\nFinal Diagnostic Data (Polars):")
print(diagnostics_df.tail(5))
