"""Triangular example — 50 iterations, 0-10, mean 5, threshold=1."""

import polars as pl
from scipy.stats import triang

import mocaco as mcc

# 50 samples from triangular(0, 10) with mode 5 (c=0.5)
vals = triang.rvs(c=0.5, loc=0, scale=10, size=50)
df = pl.DataFrame({"value": vals})

# API
mcc.methods()
mcc.describe("clt_absolute")

samples = mcc.samples(df, target_col="value")
result = mcc.convergence.clt_absolute(
    samples,
    threshold=1.0,
    eval_frequency=5,
)
with pl.Config(tbl_rows=-1):
    print(result.method)
    print(result.is_converged)
    print(result)
