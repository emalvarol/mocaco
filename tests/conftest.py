"""Shared fixtures for catable tests."""

from __future__ import annotations

import polars as pl
import pytest
from scipy.stats import triang


@pytest.fixture
def triangular_50() -> pl.DataFrame:
    """Triangular 0-10, mode 5 (c=0.5), 50 rows, deterministic seed 0."""
    r_vals = triang.rvs(c=0.5, loc=0, scale=10, size=50, random_state=0)
    return pl.DataFrame({"it": list(range(50)), "value": r_vals.tolist()})


def make_triangular_df(n: int = 50, seed: int = 0) -> pl.DataFrame:
    r_vals = triang.rvs(c=0.5, loc=0, scale=10, size=n, random_state=seed)
    return pl.DataFrame({"it": list(range(n)), "value": r_vals.tolist()})
