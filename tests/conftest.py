"""Shared fixtures for mocaco tests."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from mocaco.methods.clt_uni_abs import InputParams
from mocaco.protocols import SampleFrame


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
    return pl.DataFrame({"it": range(1, 11), "value": [5.0] * 10})


@pytest.fixture
def sample_df_with_it() -> pl.DataFrame:
    """DataFrame with explicit iteration column."""
    return pl.DataFrame({"it": range(1, 21), "measurement": [float(i) for i in range(1, 21)]})


@pytest.fixture
def sample_df_no_it() -> pl.DataFrame:
    """DataFrame without iteration column (it will be auto-created)."""
    return pl.DataFrame({"value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]})


@pytest.fixture
def sample_frame(sample_df_with_it: pl.DataFrame) -> SampleFrame:
    """Pre-built SampleFrame instance."""
    return SampleFrame(df=sample_df_with_it, target_col="measurement")


@pytest.fixture
def sample_df_no_it_frame(sample_df_no_it: pl.DataFrame) -> SampleFrame:
    """SampleFrame constructed from DataFrame without it_col."""
    return SampleFrame(df=sample_df_no_it, target_col="value")


@pytest.fixture
def clt_params() -> InputParams:
    """Default CLTAbsoluteParams instance."""
    return InputParams(threshold=0.1, confidence_level=0.95)
