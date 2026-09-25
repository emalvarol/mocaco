from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import polars as pl

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
    it_col: str
    target_col: str

    def __post_init__(self) -> None:
        missing = [
            col
            for col in (self.it_col, self.target_col)
            if col not in self.df.columns
        ]

        if missing:
            raise ValueError(
                f"Columns not found in DataFrame: {missing}. "
                f"Available columns: {self.df.columns}"
            )

        if self.df.is_empty():
            raise ValueError("The sample DataFrame cannot be empty.")


class Criterion(Protocol):
    """
    Structural contract implemented by every convergence criterion.
    """

    name: str
    description: str
    params_type: type[Any]

    def run(
        self,
        samples: SampleFrame,
        params: Any,
    ) -> "ConvergenceResult":
        ...
