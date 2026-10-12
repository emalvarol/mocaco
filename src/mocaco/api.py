"""Main module to define the API behaviour and usage."""

from __future__ import annotations

import time
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from . import methods as _methods  # noqa: F401
from .protocols import SampleFrame
from .registry import registry
from .result import ConvergenceResult, GroupedConvergenceResult

if TYPE_CHECKING:
    from collections.abc import Callable

    import polars as pl

    from .protocols import Criterion


def samples(
    df: pl.DataFrame,
    *,
    target_col: str,
    it_col: str | None = None,
    group_cols: str | list[str] | None = None
) -> SampleFrame:
    """
    Create the normalized and frozen data representation used by convergence criteria.

    This prevents input errors and ensure the input data is read-only and is
    never modified accidentally.

    Parameters
    ----------
    df
        Source Polars DataFrame.
    target_col
        Column containing the quantity to analyze.
    it_col
        Optional column containing the iteration/order of the samples. If the user omit it, it
        is automatically completed.
    group_cols
        Optional column(s) identifying independent groups for grouped convergence analysis.
    """
    return SampleFrame(
        df=df,
        target_col=target_col,
        it_col=it_col,
        group_cols=group_cols
    )


class Convergence:
    """
    Callable namespace exposing registered convergence criteria as attributes.

    Use as ``convergence(samples, method="...", **kwargs)`` for generic calls,
    or ``convergence.clt_absolute(samples, threshold=...)`` for typed calls.
    """

    def _execute_criterion(
        self,
        criterion: Criterion,
        samples: SampleFrame,
        kwargs: dict[str, Any],
    ) -> ConvergenceResult | GroupedConvergenceResult:
        start_time = time.perf_counter()

        params = criterion.params_type(**kwargs)
        result = criterion.run(samples=samples, params=params)

        elapsed = time.perf_counter() - start_time

        if isinstance(result, dict):
            n_groups = len(result)
            per_group_elapsed = elapsed / n_groups if n_groups > 0 else elapsed

            grouped_dict = GroupedConvergenceResult(
                {
                    group_key: replace(res, execution_time_sec=per_group_elapsed)
                    for group_key, res in result.items()
                }
            )
            return grouped_dict

        return replace(result, execution_time_sec=elapsed)

    def __call__(
        self,
        samples: SampleFrame,
        *,
        method: str,
        **kwargs: Any,
    ) -> ConvergenceResult | GroupedConvergenceResult:
        """Invoke a registered convergence criterion generically by name."""
        criterion = registry.get(method)
        return self._execute_criterion(criterion, samples, kwargs)

    def __getattr__(
        self, name: str
    ) -> Callable[..., ConvergenceResult | GroupedConvergenceResult]:
        """Resolve registered criteria as callable attributes."""
        criterion = registry.get(name)

        def _method(
            samples: SampleFrame, **kwargs: Any
        ) -> ConvergenceResult | GroupedConvergenceResult:
            return self._execute_criterion(criterion, samples, kwargs)

        return _method


convergence = Convergence()


def methods() -> tuple[str, ...]:
    """Return the names of all registered convergence criteria."""
    return registry.names()


def describe(name: str) -> None:
    """Return metadata and parameter information for a criterion."""
    return registry.describe(name)
