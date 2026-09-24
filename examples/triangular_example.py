"""Triangular example — 50 iterations, 0-10, mean 5, threshold=1."""

from __future__ import annotations

import polars as pl
from scipy.stats import triang

# import registers df.convergence.* namespace
import catable  # noqa: F401
from catable.convergence import clt_absolute

# 50 samples from triangular(0, 10) with mode 5 (c=0.5)
vals = triang.rvs(c=0.5, loc=0, scale=10, size=50, random_state=0)
df = pl.DataFrame({"it": list(range(50)), "value": vals.tolist()})

print("Input head:")
print(df.head(5))

# Functional API — ty-friendly
print("\nFunctional API:")
result_fn = clt_absolute(
    df, it_col="it", target_col="value", epsilon=0.1, alpha=0.05, threshold=1.0
)
print(result_fn)

# Polars namespace API — df.convergence.*
print("\nNamespace API:")
result_ns = df.convergence.clt_absolute(  # ty: ignore[unresolved-attribute]
    "it", "value", epsilon=0.1, alpha=0.05, threshold=1.0
)
print(result_ns)

# Show only converged rows
print("\nConverged rows (threshold=1.0):")
print(result_ns.filter(pl.col("converged")))
