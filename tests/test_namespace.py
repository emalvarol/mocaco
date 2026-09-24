from __future__ import annotations

import polars as pl

import catable  # noqa: F401  — registers namespace
from tests.conftest import make_triangular_df


def test_namespace_exists():
    df = make_triangular_df(10)
    assert hasattr(df, "convergence")
    assert hasattr(df.convergence, "clt_absolute")


def test_namespace_callable_returns_table():
    df = make_triangular_df(50, seed=0)
    out = df.convergence.clt_absolute(  # ty: ignore[unresolved-attribute]
        it_col="it", target_col="value", epsilon=0.1, alpha=0.05, threshold=1.0
    )
    assert isinstance(out, pl.DataFrame)
    assert out.columns == ["it", "criterion", "converged"]
    assert out.height == 50
    assert out["criterion"].unique().to_list() == ["clt_absolute"]


def test_namespace_matches_functional_api():
    from catable.convergence import clt_absolute

    df = make_triangular_df(50, seed=1)
    via_ns = df.convergence.clt_absolute(  # ty: ignore[unresolved-attribute]
        "it", "value", threshold=1.0
    )
    via_fn = clt_absolute(df, it_col="it", target_col="value", threshold=1.0)
    assert via_ns.equals(via_fn)
