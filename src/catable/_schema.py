"""Single validation module for catable.

Currently validates that a Polars DataFrame contains the required iteration
and target columns. Pydantic is used for param validation inside each
criterion module; this file only handles frame-level checks so the
public API stays small.
"""

from __future__ import annotations

import polars as pl
from pydantic import BaseModel, ConfigDict


class FrameColumns(BaseModel):
    """Minimal schema for a Monte Carlo frame.

    Kept for future extension; right now only the column names are checked.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    it_col: str = "it"
    target_col: str = "value"


def validate_frame_has_cols(
    df: pl.DataFrame,
    it_col: str = "it",
    target_col: str = "value",
) -> None:
    """Validate that *df* contains *it_col* and *target_col*.

    Raises:
        ValueError: if any required column is missing.
        TypeError: if *df* is not a Polars DataFrame.
    """
    if not isinstance(df, pl.DataFrame):
        raise TypeError(f"expected polars DataFrame, got {type(df).__name__}")

    cols = df.columns
    missing = [c for c in (it_col, target_col) if c not in cols]
    if missing:
        raise ValueError(
            f"missing required column(s) {missing} — "
            f"got columns {cols!r}, expected it_col={it_col!r} and target_col={target_col!r}"
        )
