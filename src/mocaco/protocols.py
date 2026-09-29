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
        """Validate columns and assign default iteration indices if missing."""
        if self.it_col is None:
            new_df = self.df.with_columns(pl.arange(1, len(self.df) + 1).alias("it"))
            object.__setattr__(self, "df", new_df)
            object.__setattr__(self, "it_col", "it")
            logger.info("it_col was None — auto-created column 'it' with sequential indices.")
            return

        missing = [col for col in (self.it_col, self.target_col) if col not in self.df.columns]

        if missing:
            raise ValueError(
                f"Columns not found in DataFrame: {missing}. Available columns: {self.df.columns}"
            )

        if self.df.is_empty():
            raise ValueError("The sample DataFrame cannot be empty.")


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
