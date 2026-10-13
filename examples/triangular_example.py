"""Triangular example — 50 iterations, 0-10, mean 5, threshold=1."""

import numpy as np
import polars as pl
from scipy.stats import triang

import mocaco as mcc

SEED = 42

# 1
df_single = pl.DataFrame(
    {
        "group": ["group_a"] * 40 + ["group_b"] * 40,
        "it": list(range(40)) + list(range(40)),
        "value": np.concatenate(
            [
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=SEED),
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=(SEED + 1)),
            ]
        ),
    }
)

samples_single = mcc.samples(
    df_single.filter(pl.col("group") == "group_b"),
    target_col="value",
    it_col="it",
)

result = mcc.convergence.clt_uni_abs(
    samples_single,
    threshold=0.1,
    eval_frequency=5,
)

with pl.Config(tbl_rows=-1):
    # Individual
    print(result.summary())

ax = result.plot.evolution(show=True)

# 1
df_single = pl.DataFrame(
    {
        "group": ["group_a"] * 40 + ["group_b"] * 40,
        "it": list(range(40)) + list(range(40)),
        "value": np.concatenate(
            [
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=SEED),
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=(SEED + 1)),
            ]
        ),
    }
)

samples_single = mcc.samples(
    df_single,
    target_col="value",
    it_col="it",
    group_cols="group",
)

result = mcc.convergence.clt_uni_abs(
    samples_single,
    threshold=0.1,
    eval_frequency=5,
)

with pl.Config(tbl_rows=-1):
    # Grouped
    print(result.n)
    print(result.error)
    print(result.estimate)
    print(result.data)
    print(result.execution_time_sec)
    print(result.summary())
    # Individual
    print(result[(("group", "group_a"),)].n)
    print(result[(("group", "group_a"),)].error)
    print(result[(("group", "group_a"),)].estimate)
    print(result[(("group", "group_a"),)].execution_time_sec)
    print(result[(("group", "group_a"),)].data)
    print(result[(("group", "group_a"),)].summary())

ax = result.plot.evolution(show=True)
ax = result[(("group", "group_a"),)].plot.evolution(show=True)

# 2
df_multi = pl.DataFrame(
    {
        "cat1": ["A"] * 80 + ["B"] * 80,
        "cat2": (["X"] * 40 + ["Y"] * 40) * 2,
        "it": list(range(40)) * 4,
        "value": np.concatenate(
            [
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=SEED),
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=(SEED + 1)),
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=(SEED + 2)),
                triang.rvs(c=0.5, loc=0, scale=10, size=40, random_state=(SEED + 3)),
            ]
        ),
    }
)

samples_multi = mcc.samples(
    df_multi,
    target_col="value",
    it_col="it",
    group_cols=["cat1", "cat2"],
)

result = mcc.convergence.clt_uni_abs(
    samples_multi,
    threshold=0.1,
    eval_frequency=5,
)

with pl.Config(tbl_rows=-1):
    # Grouped
    print(result.n)
    print(result.error)
    print(result.error_by(keep=["cat1"]))
    print(result.estimate)
    print(result.data)
    print(result.execution_time_sec)
    print(result.summary())
    # Individual
    print(result[(("cat1", "A"), ("cat2", "X"))].n)
    print(result[(("cat1", "A"), ("cat2", "X"))].error)
    print(result[(("cat1", "A"), ("cat2", "X"))].estimate)
    print(result[(("cat1", "A"), ("cat2", "X"))].execution_time_sec)
    print(result[(("cat1", "A"), ("cat2", "X"))].data)
    print(result[(("cat1", "A"), ("cat2", "X"))].summary())

ax = result[(("cat1", "A"), ("cat2", "X"))].plot.evolution(show=True)
