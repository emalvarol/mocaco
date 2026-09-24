from __future__ import annotations

import polars as pl
import pytest

from catable._schema import validate_frame_has_cols


def test_validate_ok():
    df = pl.DataFrame({"it": [0, 1], "value": [1.0, 2.0]})
    validate_frame_has_cols(df, it_col="it", target_col="value")  # should not raise


def test_validate_missing_it():
    df = pl.DataFrame({"value": [1.0, 2.0]})
    with pytest.raises(ValueError, match="missing required"):
        validate_frame_has_cols(df, it_col="it", target_col="value")


def test_validate_missing_value():
    df = pl.DataFrame({"it": [0, 1]})
    with pytest.raises(ValueError, match="missing required"):
        validate_frame_has_cols(df, it_col="it", target_col="value")


def test_validate_wrong_type():
    with pytest.raises(TypeError):
        validate_frame_has_cols(
            "not a df",  # ty: ignore[invalid-argument-type]  # type: ignore[arg-type]
            it_col="it",
            target_col="value",
        )
