"""Tests for SampleFrame protocol."""
# uv run pytest tests/test_protocols.py

import polars as pl
import pytest

from mocaco.protocols import SampleFrame


def test_sample_frame_creation_with_it_col(sample_df_with_it: pl.DataFrame) -> None:
    """Valid construction with explicit it_col."""
    sf = SampleFrame(df=sample_df_with_it, target_cols="measurement", it_col="it")
    assert sf.it_col == "it"


def test_sample_frame_creation_without_it_col(sample_df_no_it: pl.DataFrame) -> None:
    """Auto-creates it column with sequential indices."""
    sf = SampleFrame(df=sample_df_no_it, target_cols="value")
    assert sf.it_col == "it"


def test_sample_frame_missing_target_col_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target_cols not in DataFrame."""
    with pytest.raises(ValueError, match="Columns not found in DataFrame"):
        SampleFrame(df=sample_df_small, target_cols="nonexistent")


def test_sample_frame_empty_df_raises() -> None:
    """ValueError on empty DataFrame."""
    with pytest.raises(ValueError, match="cannot be empty"):
        SampleFrame(df=pl.DataFrame({"it": [], "value": []}), target_cols="value")


def test_sample_frame_non_numeric_target_raises() -> None:
    """TypeError when target is non-numeric."""
    df = pl.DataFrame(
        {"it": range(1, 11), "name": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]}
    )
    with pytest.raises(TypeError, match=r"(?i)numeric"):
        SampleFrame(df=df, target_cols="name")


def test_sample_frame_non_numeric_it_raises(sample_df_small: pl.DataFrame) -> None:
    """TypeError when it_col is non-numeric."""
    df = pl.DataFrame(
        {"it": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"], "value": [1.0] * 10}
    )
    with pytest.raises(TypeError, match=r"(?i)numeric"):
        SampleFrame(df=df, target_cols="value", it_col="it")


def test_sample_frame_null_values_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target contains nulls."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0, None, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}
    )
    with pytest.raises(ValueError, match=r"(?i)null|none"):
        SampleFrame(df=df, target_cols="value")


def test_sample_frame_nan_values_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target contains NaN (float dtype)."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0, float("nan"), 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}
    )
    with pytest.raises(ValueError, match=r"(?i)nan"):
        SampleFrame(df=df, target_cols="value")


def test_sample_frame_inf_values_raises(sample_df_small: pl.DataFrame) -> None:
    """ValueError when target contains Inf."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0, float("inf"), 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]}
    )
    with pytest.raises(ValueError, match=r"(?i)inf"):
        SampleFrame(df=df, target_cols="value")


def test_sample_frame_frozen() -> None:
    """Immutability: cannot reassign fields."""
    df = pl.DataFrame({"it": range(1, 11), "value": [1.0] * 10})
    sf = SampleFrame(df=df, target_cols="value", it_col="it")

    with pytest.raises(AttributeError):
        sf.target_cols = ["new_value"]  # type: ignore[misc]


def test_sample_frame_int_target_accepted(sample_df_with_it: pl.DataFrame) -> None:
    """Integer target column is valid."""
    df = pl.DataFrame({"it": range(1, 11), "target": range(10)})
    sf = SampleFrame(df=df, target_cols="target", it_col="it")
    assert sf.target_cols == ["target"]


def test_sample_frame_filter_cols(sample_df_with_it: pl.DataFrame) -> None:
    """SampleFrame validates columns are present."""
    df = pl.DataFrame(
        {"it": range(1, 11), "value": [1.0] * 10, "extra": [9.0] * 10, "another": [1.0] * 10}
    )
    sf = SampleFrame(df=df, target_cols="value", it_col="it")
    assert sf.it_col == "it"
    assert sf.target_cols == ["value"]


def test_sample_frame_target_cols_str_normalized() -> None:
    """A string target_cols is normalized to a one-element list."""
    df = pl.DataFrame({"value": [1.0] * 30})
    sf = SampleFrame(df=df, target_cols="value")
    assert sf.target_cols == ["value"]


def test_sample_frame_target_cols_list_preserved() -> None:
    """A list of target columns is preserved as a list."""
    df = pl.DataFrame({"a": [1.0] * 30, "b": [2.0] * 30})
    sf = SampleFrame(df=df, target_cols=["a", "b"])
    assert sf.target_cols == ["a", "b"]


def test_sample_frame_target_cols_empty_raises() -> None:
    """ValueError when target_cols is an empty list."""
    df = pl.DataFrame({"value": [1.0] * 30})
    with pytest.raises(ValueError, match="at least one"):
        SampleFrame(df=df, target_cols=[])


def test_sample_frame_target_cols_duplicates_raise() -> None:
    """ValueError when target_cols repeats a column name."""
    df = pl.DataFrame({"a": [1.0] * 30, "b": [2.0] * 30})
    with pytest.raises(ValueError, match="duplicate"):
        SampleFrame(df=df, target_cols=["a", "b", "a"])


def test_sample_frame_missing_target_col_in_list_raises() -> None:
    """ValueError when one of the target columns is missing."""
    df = pl.DataFrame({"it": range(1, 11), "a": [1.0] * 10, "b": [2.0] * 10})
    with pytest.raises(ValueError, match="Columns not found in DataFrame"):
        SampleFrame(df=df, target_cols=["a", "missing"])


def test_sample_frame_non_numeric_target_in_list_raises() -> None:
    """TypeError when one of the target columns is non-numeric."""
    df = pl.DataFrame({"it": range(1, 11), "a": [1.0] * 10, "name": ["x"] * 10})
    with pytest.raises(TypeError, match=r"(?i)numeric"):
        SampleFrame(df=df, target_cols=["a", "name"])


def test_sample_frame_null_values_in_list_raises() -> None:
    """ValueError when one of the target columns contains nulls."""
    df = pl.DataFrame(
        {
            "it": range(1, 11),
            "a": [1.0] * 10,
            "b": [1.0, None, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        }
    )
    with pytest.raises(ValueError, match=r"(?i)null|none"):
        SampleFrame(df=df, target_cols=["a", "b"])


def test_sample_frame_group_cols_str_normalized() -> None:
    """A string group_cols is normalized to a one-element list."""
    df = pl.DataFrame({"group": ["a"] * 30, "value": [1.0] * 30})
    sf = SampleFrame(df=df, target_cols="value", group_cols="group")
    assert sf.group_cols == ["group"]


def test_sample_frame_group_cols_list_preserved() -> None:
    """A list of group columns is preserved as a list."""
    df = pl.DataFrame({"a": ["x"] * 30, "b": ["y"] * 30, "value": [1.0] * 30})
    sf = SampleFrame(df=df, target_cols="value", group_cols=["a", "b"])
    assert sf.group_cols == ["a", "b"]


def test_sample_frame_group_cols_none_becomes_empty() -> None:
    """None group_cols is normalized to an empty list."""
    df = pl.DataFrame({"value": [1.0] * 30})
    sf = SampleFrame(df=df, target_cols="value")
    assert sf.group_cols == []


def test_sample_frame_group_cols_auto_it_per_group() -> None:
    """The auto-created it column restarts at 1 within each group."""
    df = pl.DataFrame({"group": ["a"] * 5 + ["b"] * 5, "value": [1.0] * 10})
    sf = SampleFrame(df=df, target_cols="value", group_cols="group")
    assert sf.df["it"].to_list() == [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]


def test_sample_frame_group_col_missing_raises() -> None:
    """ColumnNotFoundError when a group column is absent."""
    df = pl.DataFrame({"group": ["a"] * 30, "value": [1.0] * 30})
    with pytest.raises(pl.exceptions.ColumnNotFoundError):
        SampleFrame(df=df, target_cols="value", group_cols="missing")


def test_sample_frame_group_col_unsupported_dtype_raises() -> None:
    """TypeError for an unsupported group column dtype."""
    df = pl.DataFrame({"group": [[1], [2]] * 5, "value": [1.0] * 10})
    with pytest.raises(TypeError, match=r"(?i)unsupported"):
        SampleFrame(df=df, target_cols="value", group_cols="group")


def test_sample_frame_group_cols_frozen() -> None:
    """group_cols is immutable after construction."""
    df = pl.DataFrame({"group": ["a"] * 30, "value": [1.0] * 30})
    sf = SampleFrame(df=df, target_cols="value", group_cols="group")
    with pytest.raises(AttributeError):
        sf.group_cols = ["other"]  # type: ignore[misc]
