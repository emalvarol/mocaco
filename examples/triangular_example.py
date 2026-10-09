"""Triangular example — 50 iterations, 0-10, mean 5, threshold=1."""

import polars as pl
from scipy.stats import triang

import mocaco as mcc

# 50 samples from triangular(0, 10) with mode 5 (c=0.5)
vals = triang.rvs(c=0.5, loc=0, scale=10, size=10_000)
df = pl.DataFrame({"value": vals})
samples = mcc.samples(df, target_col="value")

# API
mcc.methods()

# 1
mcc.describe("clt_uni_abs")
result = mcc.convergence.clt_uni_abs(
    samples,
    threshold=0.1,
    eval_frequency=5,
)
with pl.Config(tbl_rows=-1):
    print(result.execution_time_sec)  # 0.001 (5_000) # 0.002 (10_000) # 0.005 (100_000)
    print(result.data)
result.summary()
ax = result.plot.evolution(show=True)
