"""Shared fixtures for mocaco tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import polars as pl
import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

from mocaco.methods.clt_multi_rel import InputParams as MultiInputParams
from mocaco.methods.clt_uni_abs import InputParams
from mocaco.methods.clt_uni_rel import InputParams as RelInputParams
from mocaco.protocols import SampleFrame
from mocaco.result import ConvergenceResult, GroupedConvergenceResult


@pytest.fixture
def sample_df_small() -> pl.DataFrame:
    """10-row Polars DataFrame with known values."""
    return pl.DataFrame(
        {"it": range(1, 11), "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}
    )


@pytest.fixture
def sample_df_large() -> pl.DataFrame:
    """500-row DataFrame with normally distributed values."""
    rng = np.random.default_rng(42)
    values = rng.standard_normal(500)
    return pl.DataFrame({"it": range(1, 501), "value": values})


@pytest.fixture
def sample_df_constant() -> pl.DataFrame:
    """DataFrame with zero variance (all values identical)."""
    return pl.DataFrame({"it": range(1, 31), "value": [5.0] * 30})


@pytest.fixture
def sample_df_with_it() -> pl.DataFrame:
    """DataFrame with explicit iteration column."""
    return pl.DataFrame({"it": range(1, 31), "measurement": [float(i) for i in range(1, 31)]})


@pytest.fixture
def sample_df_no_it() -> pl.DataFrame:
    """DataFrame without iteration column (it will be auto-created)."""
    return pl.DataFrame({"value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]})


@pytest.fixture
def sample_frame(sample_df_with_it: pl.DataFrame) -> SampleFrame:
    """Pre-built SampleFrame instance."""
    return SampleFrame(df=sample_df_with_it, target_cols="measurement")


@pytest.fixture
def sample_df_no_it_frame(sample_df_no_it: pl.DataFrame) -> SampleFrame:
    """SampleFrame constructed from DataFrame without it_col."""
    return SampleFrame(df=sample_df_no_it, target_cols="value")


@pytest.fixture
def clt_params() -> InputParams:
    """Default CLTAbsoluteParams instance."""
    return InputParams(threshold=0.1, confidence_level=0.95)


@pytest.fixture
def clt_rel_params() -> RelInputParams:
    """Default relative-criterion InputParams instance."""
    return RelInputParams(threshold=0.05, confidence_level=0.95)


@pytest.fixture
def clt_multi_params() -> MultiInputParams:
    """Default multivariate-criterion InputParams instance."""
    return MultiInputParams(threshold=0.1, confidence_level=0.95)


@pytest.fixture
def sample_df_multi_target() -> pl.DataFrame:
    """300-row DataFrame with two correlated target columns and an iteration column."""
    rng = np.random.default_rng(3)
    return pl.DataFrame(
        {
            "it": range(1, 301),
            "a": rng.standard_normal(300),
            "b": rng.standard_normal(300),
        }
    )


@pytest.fixture
def sample_frame_multi_target(sample_df_multi_target: pl.DataFrame) -> SampleFrame:
    """Pre-built SampleFrame with two target columns."""
    return SampleFrame(df=sample_df_multi_target, target_cols=["a", "b"])


@pytest.fixture
def sample_frame_constant(sample_df_constant: pl.DataFrame) -> SampleFrame:
    """Pre-built SampleFrame over a zero-variance DataFrame."""
    return SampleFrame(df=sample_df_constant, target_cols="value")


@pytest.fixture
def sample_df_grouped() -> pl.DataFrame:
    """80-row DataFrame with two independent groups of 40 rows each."""
    rng = np.random.default_rng(7)
    return pl.DataFrame(
        {
            "group": ["a"] * 40 + ["b"] * 40,
            "it": list(range(1, 41)) * 2,
            "value": rng.standard_normal(80) + 5.0,
        }
    )


@pytest.fixture
def sample_df_grouped_multi() -> pl.DataFrame:
    """160-row DataFrame with a 2x2 group grid of 40 rows each."""
    rng = np.random.default_rng(11)
    return pl.DataFrame(
        {
            "cat1": ["A"] * 80 + ["B"] * 80,
            "cat2": (["X"] * 40 + ["Y"] * 40) * 2,
            "it": list(range(1, 41)) * 4,
            "value": rng.standard_normal(160) + 5.0,
        }
    )


@pytest.fixture
def sample_frame_grouped(sample_df_grouped: pl.DataFrame) -> SampleFrame:
    """SampleFrame with a single group column."""
    return SampleFrame(df=sample_df_grouped, target_cols="value", group_cols="group")


@pytest.fixture
def sample_frame_grouped_multi(sample_df_grouped_multi: pl.DataFrame) -> SampleFrame:
    """SampleFrame with two group columns."""
    return SampleFrame(
        df=sample_df_grouped_multi, target_cols="value", group_cols=["cat1", "cat2"]
    )


@pytest.fixture
def make_convergence_result() -> Callable[..., ConvergenceResult]:
    """Build a ConvergenceResult with sensible defaults for result tests."""

    def _make(
        *,
        n: int = 40,
        estimate: float | None = 1.0,
        error: float | None = 0.1,
        is_converged: bool | None = True,
        method: str = "clt_uni_abs",
        error_col: str = "abs_error",
    ) -> ConvergenceResult:
        return ConvergenceResult(
            method=method,
            n=n,
            n_col="n",
            estimate=estimate,
            estimate_col="mean",
            error=error,
            error_col=error_col,
            is_converged=is_converged,
            is_converged_col="is_converged",
            data=pl.DataFrame(
                {
                    "n": [n],
                    "mean": [estimate],
                    error_col: [error],
                    "is_converged": [is_converged],
                }
            ),
        )

    return _make


@pytest.fixture
def grouped_result(
    make_convergence_result: Callable[..., ConvergenceResult],
) -> GroupedConvergenceResult:
    """Build a grouped result with two groups under a single group column."""
    return GroupedConvergenceResult(
        {
            (("group", "a"),): make_convergence_result(n=40, error=0.1),
            (("group", "b"),): make_convergence_result(n=60, error=0.2),
        }
    )
