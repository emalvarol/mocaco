"""Tests for SampleFrame protocol."""
# uv run pytest tests/test_protocols.py

import polars as pl
import pytest

from mocaco.protocols import SampleFrame


def test_sample_frame_creation_with_it_col(sample_df_with_it: pl.DataFrame) -> None:
    """Valid construction with explicit it_col."""
    sf = SampleFrame(df=sample_df_with_it, target_col="measurement", it_col="it")
    assert sf.it_col == "it"


def test_sample_frame_creation_without_it_col(sample_df_no_it: pl.DataFrame) -> None:
    """Auto-creates it column with sequential indices."""
    sf = SampleFrame(df=sample_df_no_it, target_col="value")
    assert sf.it_col == "it"


def test_sample_frame_missing_target_col_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target_col not in DataFrame."""
    with pytest.raises(ValueError, match="Columns not found in DataFrame"):
        SampleFrame(df=sample_df_small, target_col="nonexistent")


def test_sample_frame_empty_df_raises() -> None:
    """ValueError on empty DataFrame."""
    with pytest.raises(ValueError, match="cannot be empty"):
        SampleFrame(df=pl.DataFrame({"it": [], "value": []}), target_col="value")


def test_sample_frame_non_numeric_target_raises() -> None:
    """TypeError when target is non-numeric."""
    df = pl.DataFrame(
        {"it": range(1, 11), "name": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]}
    )
    with pytest.raises(TypeError, match=r"(?i)numeric"):
        SampleFrame(df=df, target_col="name")


def test_sample_frame_non_numeric_it_raises(sample_df_small: pl.DataFrame) -> None:
    """TypeError when it_col is non-numeric."""
    df = pl.DataFrame(
        {"it": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"], "value": [1.0] * 10}
    )
    with pytest.raises(TypeError, match=r"(?i)numeric"):
        SampleFrame(df=df, target_col="value", it_col="it")


def test_sample_frame_null_values_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target contains nulls."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0, None, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}
    )
    with pytest.raises(ValueError, match=r"(?i)null|none"):
        SampleFrame(df=df, target_col="value")


def test_sample_frame_nan_values_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target contains NaN (float dtype)."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0, float("nan"), 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}
    )
    with pytest.raises(ValueError, match=r"(?i)nan"):
        SampleFrame(df=df, target_col="value")


def test_sample_frame_inf_values_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target contains Inf."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0, float("inf"), 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}
    )
    with pytest.raises(ValueError, match=r"(?i)inf"):
        SampleFrame(df=df, target_col="value")


def test_sample_frame_frozen() -> None:
    """Immutability: cannot reassign fields."""
    df = pl.DataFrame({"it": range(1, 11), "value": [1.0] * 10})
    sf = SampleFrame(df=df, target_col="value", it_col="it")

    with pytest.raises(AttributeError):
        sf.target_col = "new_value"  # type: ignore[misc]


def test_sample_frame_int_target_accepted(sample_df_with_it: pl.DataFrame) -> None:
    """Integer target column is valid."""
    df = pl.DataFrame({"it": range(1, 11), "target": range(10)})
    sf = SampleFrame(df=df, target_col="target", it_col="it")
    assert sf.target_col == "target"


def test_sample_frame_filter_cols(sample_df_with_it: pl.DataFrame) -> None:
    """SampleFrame validates columns are present."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0] * 10, "extra": [9.0] * 10, "another": [1.0] * 10}
    )
    sf = SampleFrame(df=df, target_col="value", it_col="it")
    assert sf.it_col == "it"
    assert sf.target_col == "value"
    # DataFrame maintains all columns; only it_col and target_col are required
