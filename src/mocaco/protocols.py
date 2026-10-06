"""Protocol for method addition and its input data format."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

import polars as pl

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .result import ConvergenceResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SampleFrame:
    """
    Normalized representation of Monte Carlo samples.

    Parameters
    ----------
    df
        Source Polars DataFrame.
    it_col
        Column containing the iteration/order of the samples.
    target_col
        Column containing the quantity to analyze.
    """

    df: pl.DataFrame
    target_col: str
    it_col: str | None = None

    def __post_init__(self) -> None:
        """Validate columns, assign default iteration indices if missing, and handle edge cases."""
        # 1. Resolve and normalize it_col name
        if self.it_col is None:
            it_col_name = "it"
            new_df = self.df.with_columns(pl.arange(1, len(self.df) + 1).alias(it_col_name))
            object.__setattr__(self, "df", new_df)
            object.__setattr__(self, "it_col", it_col_name)
            logger.info("it_col was None — auto-created column 'it' with sequential indices.")
        else:
            it_col_name = self.it_col

        # 2. Validate structural integrity (it_col_name is guaranteed to be str here)
        missing = [col for col in (it_col_name, self.target_col) if col not in self.df.columns]
        if missing:
            raise ValueError(
                f"Columns not found in DataFrame: {missing}. Available columns: {self.df.columns}"
            )

        if self.df.is_empty():
            raise ValueError("The sample DataFrame cannot be empty.")

        # 3. Validate Data Types (it_col and target_col must be numeric)
        it_dtype = self.df.get_column(it_col_name).dtype
        if not it_dtype.is_numeric():
            raise TypeError(
                f"Iteration column '{it_col_name}' must be numeric (int or float), got {it_dtype}."
            )

        target = self.df.get_column(self.target_col)
        if not target.dtype.is_numeric():
            raise TypeError(
                f"Target column '{self.target_col}' must be numeric (int or float), got {target.dtype}."
            )

        # 4. Input validation and edge case handling (Null, NaN, Inf)
        if target.is_null().any():
            raise ValueError(f"Target column '{self.target_col}' contains Null (missing) values.")

        if target.dtype in (pl.Float32, pl.Float64):
            if target.is_nan().any():
                raise ValueError(f"Target column '{self.target_col}' contains NaN values.")
            if target.is_infinite().any():
                raise ValueError(f"Target column '{self.target_col}' contains Infinite (Inf) values.")

class Criterion(Protocol):
    """Structural contract implemented by every convergence criterion."""

    name: str
    supports_eval_frequency: bool
    description: str
    params_type: type[Any]

    assumptions: ClassVar[Sequence[str]]
    limitations: ClassVar[Sequence[str]]
    result_interpretation: str
    example_usage: str
    references: ClassVar[Sequence[str]]

    def run(
        self,
        samples: SampleFrame,
        params: Any,
    ) -> ConvergenceResult: ...
