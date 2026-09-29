from __future__ import annotations

import polars as pl

from .protocols import SampleFrame
from .result import ConvergenceResult

def samples(df: pl.DataFrame, *, target_col: str, it_col: str | None = None) -> SampleFrame: ...
def methods() -> tuple[str, ...]: ...
def describe(name: str) -> dict | None: ...

class Convergence:
    def __call__(self, samples: SampleFrame, *, method: str, **kwargs) -> ConvergenceResult: ...
    def clt_absolute(
        self,
        samples: SampleFrame,
        *,
        threshold: float,
        confidence_level: float = 0.95,
        eval_frequency: int = 1,
    ) -> ConvergenceResult:
        """
        Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold.

        Parameters
        ----------
        threshold : float
            Maximum accepted absolute Monte Carlo error.
        confidence_level : float, default 0.95
            Confidence level used for the CLT margin of error.
        eval_frequency : int, default 1
            Number of rows between successive evaluations.
        """
        ...

convergence: Convergence
