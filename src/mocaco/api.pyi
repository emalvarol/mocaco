from __future__ import annotations

from typing import Any

import polars as pl

from .protocols import SampleFrame
from .result import ConvergenceResult, GroupedConvergenceResult

def samples(
    df: pl.DataFrame,
    *,
    target_col: str | list[str],
    it_col: str | None = None,
    group_cols: str | list[str] | None = None,
) -> SampleFrame: ...
def methods() -> tuple[str, ...]: ...
def describe(name: str) -> None: ...

class Convergence:
    def __call__(
        self, samples: SampleFrame, *, method: str, **kwargs: Any
    ) -> ConvergenceResult | GroupedConvergenceResult: ...
    def clt_multi_rel(
        self,
        samples: SampleFrame,
        *,
        alpha: float = 0.05,
        epsilon: float,
        eval_frequency: int | None = None,
        warm_up_period: int = 100,
    ) -> ConvergenceResult | GroupedConvergenceResult:
        """
        Multivariate Central Limit Theorem based convergence criterion using a relative confidence-region volume tolerance (Vats et al., 2019).

        Parameters
        ----------
        alpha : float, default 0.05
            Significance level of the Hotelling F-based confidence region that builds the left-hand side of the rule (the confidence-region radius, i.e. the error). The confidence level is 1 - alpha.
        epsilon : float
            Relative tolerance applied to the natural scale of the target distribution, det(cov)^(1/(2p)). It defines the threshold rhs = epsilon * det(cov)^(1/(2p)); convergence requires the confidence-region radius (error) to fall below it.
        eval_frequency : int | None, default None
            Step interval (in iterations) between convergence checkpoints. If None, the criterion is evaluated once at the final sample.
        warm_up_period : int, default 100
            Warm-up sample size (n*) before which convergence is never declared and at which the first checkpoint is taken. Values below 100 emit a warning.
        """
        ...
    def clt_uni_abs(
        self,
        samples: SampleFrame,
        *,
        threshold: float,
        confidence_level: float = 0.95,
        eval_frequency: int | None = None,
    ) -> ConvergenceResult | GroupedConvergenceResult:
        """
        Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold.

        Parameters
        ----------
        threshold : float
            Maximum accepted absolute Monte Carlo error.
        confidence_level : float, default 0.95
            Confidence level used for the CLT margin of error.
        eval_frequency : int | None, default None
            Step interval for periodic evaluation of convergence history natively in Polars.
        """
        ...
    def clt_uni_rel(
        self,
        samples: SampleFrame,
        *,
        threshold: float,
        confidence_level: float = 0.95,
        eval_frequency: int | None = None,
    ) -> ConvergenceResult | GroupedConvergenceResult:
        """
        Central Limit Theorem based convergence criterion using a relative Monte Carlo error threshold.

        Parameters
        ----------
        threshold : float
            Maximum accepted relative Monte Carlo error (proportion of estimate).
        confidence_level : float, default 0.95
            Confidence level used for the CLT margin of error.
        eval_frequency : int | None, default None
            Step interval for periodic evaluation of convergence history natively in Polars.
        """
        ...

convergence: Convergence
