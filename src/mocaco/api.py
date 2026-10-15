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
    target_col: str | list[str],
    it_col: str | None = None,
    group_cols: str | list[str] | None = None,
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
        Column, or list of columns, containing the quantity/quantities to analyze.
    it_col
        Optional column containing the iteration/order of the samples. If the user omit it, it
        is automatically completed.
    group_cols
        Optional column(s) identifying independent groups for grouped convergence analysis.
    """
    return SampleFrame(df=df, target_cols=target_col, it_col=it_col, group_cols=group_cols)


class Convergence:
    """
    Callable namespace exposing registered convergence criteria as attributes.

    Use as ``convergence(samples, method="...", **kwargs)`` for generic calls,
    or ``convergence.clt_absolute(samples, threshold=...)`` for typed calls.
    """

    @staticmethod
    def _validate_dimensionality(criterion: Criterion, samples: SampleFrame) -> None:
        """Ensure the criterion dimensionality matches the number of target columns."""
        target_cols = samples.target_cols
        n_targets = 1 if isinstance(target_cols, str) else len(target_cols)
        dimensionality = criterion.dimensionality

        if dimensionality == "univariate" and n_targets != 1:
            raise ValueError(
                f"Criterion '{criterion.name}' is univariate but received {n_targets} "
                "target columns. Provide exactly one 'target_col'."
            )

        if dimensionality == "multivariate" and n_targets < 2:
            raise ValueError(
                f"Criterion '{criterion.name}' is multivariate but received {n_targets} "
                "target column(s). Provide at least two target columns via 'target_col'."
            )

    def _execute_criterion(
        self,
        criterion: Criterion,
        samples: SampleFrame,
        kwargs: dict[str, Any],
    ) -> ConvergenceResult | GroupedConvergenceResult:
        start_time = time.perf_counter()

        self._validate_dimensionality(criterion, samples)

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

    def __getattr__(self, name: str) -> Callable[..., ConvergenceResult | GroupedConvergenceResult]:
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
