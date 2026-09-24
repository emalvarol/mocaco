"""Tests for clt_absolute — triangular 0-10 mean 5, up to 50 iterations."""

from __future__ import annotations

import polars as pl
import pytest
from scipy.stats import triang

import catable  # noqa: F401 — registers namespace
from catable.convergence import clt_absolute


def _triangular_df(n: int = 50, seed: int = 0) -> pl.DataFrame:
    vals = triang.rvs(c=0.5, loc=0, scale=10, size=n, random_state=seed)
    return pl.DataFrame({"it": list(range(n)), "value": vals.tolist()})


def test_clt_absolute_triangular_50_threshold_1():
    """50 iterations, threshold=1 — table has 50 rows, cols it|criterion|converged."""
    df = _triangular_df(50, seed=0)
    out = clt_absolute(df, it_col="it", target_col="value", epsilon=0.1, alpha=0.05, threshold=1.0)
    assert out.columns == ["it", "criterion", "converged"]
    assert out.height == 50
    # converged is boolean
    assert out["converged"].dtype == pl.Boolean
    # criterion column is constant
    assert (out["criterion"] == "clt_absolute").all()
    # it column preserved
    assert out["it"].to_list() == list(range(50))
    # with threshold=1, early n -> not converged, later n -> converged
    # half_width at n=50 ~ z*sigma/sqrt(50) ~0.6 <1 so last row True
    assert out["converged"][-1] is True
    # at n=1 should be False (std undefined)
    assert out["converged"][0] is False


def test_clt_absolute_via_namespace_threshold_1():
    df = _triangular_df(50, seed=0)
    out = df.convergence.clt_absolute(  # ty: ignore[unresolved-attribute]
        "it", "value", epsilon=0.1, alpha=0.05, threshold=1.0
    )
    assert out.height == 50
    assert out["converged"][-1] is True


def test_clt_absolute_strict_threshold_never_converges():
    df = _triangular_df(50, seed=0)
    out = clt_absolute(df, threshold=0.01)  # very strict
    # with sigma~2, half_width ~0.6 >0.01 => never converged
    assert out["converged"].sum() == 0


def test_clt_absolute_loose_threshold_all_converged_eventually():
    df = _triangular_df(50, seed=0)
    out = clt_absolute(df, threshold=10.0)
    # large threshold => even n=2 should be converged after a few steps
    # n=1 is always False, so not all True, but last must be True
    assert out["converged"][-1] is True


def test_clt_absolute_missing_col_raises():
    df = pl.DataFrame({"it": [0, 1], "x": [1.0, 2.0]})
    with pytest.raises(ValueError, match="missing required"):
        clt_absolute(df, it_col="it", target_col="value", threshold=1.0)


def test_clt_absolute_custom_cols():
    df = pl.DataFrame({"iter": [0, 1, 2, 3], "obs": [1.0, 2.0, 3.0, 4.0]})
    out = clt_absolute(df, it_col="iter", target_col="obs", threshold=5.0)
    assert out.columns == ["it", "criterion", "converged"]
    assert out.height == 4
