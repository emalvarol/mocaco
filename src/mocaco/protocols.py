"""Protocol for method addition and its input data format."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Protocol

import polars as pl

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .result import ConvergenceResult, GroupedConvergenceResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SampleFrame:
    """
    Normalized representation of Monte Carlo samples.

    Parameters
    ----------
    df
        Source Polars DataFrame.
    target_cols
        Column(s) containing the quantity/quantities to analyze. Accepts a single
        column name or a list of column names; normalized to ``list[str]``.
    it_col
        Optional column containing the iteration/order of the samples.
    group_cols
        Optional column(s) identifying independent groups for grouped convergence analysis.
    """

    df: pl.DataFrame
    target_cols: str | list[str]
    it_col: str | None = None
    group_cols: str | list[str] | None = None

    def __post_init__(self) -> None:
        """Validate columns, assign default iteration indices if missing, and handle edge cases."""
        # Normalize target_cols to a non-empty, duplicate-free list[str]
        if isinstance(self.target_cols, str):
            targets = [self.target_cols]
        else:
            targets = list(self.target_cols)

        if not targets:
            raise ValueError("target_cols must contain at least one column name.")
        if len(set(targets)) != len(targets):
            raise ValueError(f"target_cols contains duplicate column names: {targets}.")

        object.__setattr__(self, "target_cols", targets)

        # Normalize group_cols to a list[str]
        if isinstance(self.group_cols, str):
            object.__setattr__(self, "group_cols", [self.group_cols])
        elif self.group_cols is None:
            object.__setattr__(self, "group_cols", [])

        # Resolve and normalize it_col name
        if self.it_col is None:
            it_col_name = "it"
            if self.group_cols:
                new_df = self.df.with_columns(
                    pl.int_range(1, pl.len() + 1).over(self.group_cols).alias(it_col_name)
                )
            else:
                new_df = self.df.with_columns(pl.int_range(1, pl.len() + 1).alias(it_col_name))
            object.__setattr__(self, "df", new_df)
            object.__setattr__(self, "it_col", it_col_name)
            logger.info(
                f"it_col was None — auto-created column '{it_col_name}' with sequential indices."
            )
        else:
            it_col_name = self.it_col

        assert isinstance(self.target_cols, list)

        # Validate structural integrity (it_col_name is guaranteed to be str here)
        missing = [col for col in (it_col_name, *self.target_cols) if col not in self.df.columns]
        if missing:
            raise ValueError(
                f"Columns not found in DataFrame: {missing}. Available columns: {self.df.columns}"
            )

        if self.df.is_empty():
            raise ValueError("The sample DataFrame cannot be empty.")

        # Validate Data Types (it_col and target_cols must be numeric)
        it_dtype = self.df.get_column(it_col_name).dtype
        if not it_dtype.is_numeric():
            raise TypeError(
                f"Iteration column '{it_col_name}' must be numeric (int or float), got {it_dtype}."
            )

        for col in self.target_cols:
            target = self.df.get_column(col)
            if not target.dtype.is_numeric():
                raise TypeError(
                    f"Target column '{col}' must be numeric (int or float), got {target.dtype}."
                )

        assert isinstance(self.group_cols, list)
        for col in self.group_cols:
            dtype = self.df.get_column(col).dtype
            if (
                not isinstance(
                    dtype,
                    (
                        pl.Int8,
                        pl.Int16,
                        pl.Int32,
                        pl.Int64,
                        pl.UInt8,
                        pl.UInt16,
                        pl.UInt32,
                        pl.UInt64,
                        pl.Float32,
                        pl.Float64,
                        pl.String,
                        pl.Categorical,
                        pl.Enum,
                        pl.Boolean,
                        pl.Date,
                        pl.Datetime,
                    ),
                )
                and not dtype.is_numeric()
            ):
                raise TypeError(
                    f"Group column '{col}' has unsupported data type {dtype}. "
                    "Supported types are numeric, string, categorical, enum, boolean, date, and datetime."
                )

        # Input validation and edge case handling (Null, NaN, Inf)
        for col in self.target_cols:
            target = self.df.get_column(col)
            if target.is_null().any():
                raise ValueError(f"Target column '{col}' contains Null (missing) values.")

            if target.dtype in (pl.Float32, pl.Float64):
                if target.is_nan().any():
                    raise ValueError(f"Target column '{col}' contains NaN values.")
                if target.is_infinite().any():
                    raise ValueError(f"Target column '{col}' contains Infinite (Inf) values.")


class Criterion(Protocol):
    """Structural contract implemented by every convergence criterion."""

    name: str
    description: str
    params_type: type[Any]
    dimensionality: ClassVar[Literal["univariate", "multivariate"]]

    assumptions: ClassVar[Sequence[str]]
    limitations: ClassVar[Sequence[str]]
    result_interpretation: str
    example_usage: str
    references: ClassVar[Sequence[str]]

    def run(
        self,
        samples: SampleFrame,
        params: Any,
    ) -> ConvergenceResult | GroupedConvergenceResult: ...
