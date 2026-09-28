from __future__ import annotations

import polars as pl
from .protocols import SampleFrame
from .result import ConvergenceResult

def samples(df: pl.DataFrame, *, it_col: str | None, target_col: str) -> SampleFrame: ...
def methods() -> tuple[str, ...]: ...
def describe(method: str) -> dict: ...

class Convergence:
    def __call__(self, samples: SampleFrame, *, method: str, **kwargs) -> ConvergenceResult: ...
    def clt_absolute(self, samples: SampleFrame, *, threshold: float, confidence_level: float = 0.95, stb_window: int = 30) -> ConvergenceResult:
        """
        Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold.

        Parameters
        ----------
        threshold : float
            Maximum accepted absolute Monte Carlo error.
        confidence_level : float, default 0.95
            Confidence level used for the CLT margin of error.
        stb_window : int, default 30
            Minimum number of consecutive iterations meeting the threshold.
        """
        ...
convergence: Convergence