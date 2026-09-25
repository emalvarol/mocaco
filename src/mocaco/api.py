from __future__ import annotations

import polars as pl

from .protocols import SampleFrame
from .registry import registry
from .result import ConvergenceResult

# Importing methods triggers registration of built-in criteria.
from . import methods as _methods  # noqa: F401


def samples(
    df: pl.DataFrame,
    *,
    it_col: str,
    target_col: str,
) -> SampleFrame:
    """
    Create the normalized representation used by convergence criteria.
    """
    return SampleFrame(
        df=df,
        it_col=it_col,
        target_col=target_col,
    )


def convergence(
    samples: SampleFrame,
    *,
    method: str,
    **kwargs,
) -> ConvergenceResult:
    """
    Run a convergence criterion by name.
    """
    criterion = registry.get(method)

    params = criterion.params_type(**kwargs)

    return criterion.run(
        samples=samples,
        params=params,
    )


def clt_absolute(
    samples: SampleFrame,
    *,
    threshold: float,
    confidence_level: float = 0.95,
    stb_window: int = 30,
) -> ConvergenceResult:
    """
    Run the CLT absolute-error convergence criterion.
    """
    return convergence(
        samples,
        method="clt_absolute",
        threshold=threshold,
        confidence_level=confidence_level,
        stb_window=stb_window,
    )


def methods() -> tuple[str, ...]:
    """Return the names of all registered convergence criteria."""
    return registry.names()


def describe(method: str) -> dict:
    """Return metadata and parameter information for a criterion."""
    return registry.describe(method)
