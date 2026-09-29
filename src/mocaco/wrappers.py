"""Criterion wrappers to expand evaluation behaviors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import polars as pl

from .protocols import SampleFrame
from .result import ConvergenceResult

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .protocols import Criterion


class CriterionWrapper:
    """
    Base class for criterion wrappers.

    A wrapper intercepts calls to a criterion's ``run()`` method to add
    cross-cutting behaviour (e.g. periodic evaluation, caching, logging)
    without modifying the criterion itself.

    All metadata attributes are delegated to the inner criterion so that
    the wrapper satisfies the same ``Criterion`` protocol.
    """

    def __init__(self, criterion: Criterion) -> None:
        self._criterion = criterion

    @property
    def name(self) -> str:
        return self._criterion.name

    @property
    def description(self) -> str:
        return self._criterion.description

    @property
    def params_type(self) -> type[Any]:
        return self._criterion.params_type

    @property
    def assumptions(self) -> Sequence[str]:
        return self._criterion.assumptions

    @property
    def limitations(self) -> Sequence[str]:
        return self._criterion.limitations

    @property
    def result_interpretation(self) -> str:
        return self._criterion.result_interpretation

    @property
    def example_usage(self) -> str:
        return self._criterion.example_usage

    @property
    def references(self) -> Sequence[str]:
        return self._criterion.references

    def run(
        self,
        samples: SampleFrame,
        params: Any,
    ) -> ConvergenceResult:
        return self._criterion.run(samples, params)


class EvalFrequencyWrapper(CriterionWrapper):
    """
    Wrapper that evaluates a criterion at regular iteration intervals.

    Instead of running the criterion once on the full dataset, this wrapper
    runs it on cumulative slices of the data at every ``eval_frequency``
    rows.  The diagnostic DataFrames from each evaluation are concatenated
    into a single DataFrame, and the final ``ConvergenceResult`` carries the
    last run's summary fields combined with the concatenated history.

    Parameters
    ----------
    criterion
        The inner criterion to wrap.
    eval_frequency
        Number of rows between successive evaluations.  Must be a
        positive integer.

    Examples
    --------
    >>> wrapper = EvalFrequencyWrapper(criterion, eval_frequency=10)
    >>> result = wrapper.run(samples, params)
    >>> result.data  # diagnostic history across all evaluations
    """

    def __init__(self, criterion: Criterion, eval_frequency: int) -> None:
        super().__init__(criterion)
        if eval_frequency <= 0:
            raise ValueError(f"eval_frequency must be a positive integer, got {eval_frequency}")
        self._eval_frequency = eval_frequency

    @property
    def eval_frequency(self) -> int:
        return self._eval_frequency

    def run(
        self,
        samples: SampleFrame,
        params: Any,
    ) -> ConvergenceResult:
        total_rows = len(samples.df)

        if self._eval_frequency >= total_rows:
            result = self._criterion.run(samples, params)
            return ConvergenceResult(
                method=result.method,
                n=result.n,
                estimate=result.estimate,
                error=result.error,
                is_converged=result.is_converged,
                data=result.data,
                diagnostics={
                    **result.diagnostics,
                    "eval_frequency": self._eval_frequency,
                    "n_evaluations": 1,
                },
            )

        eval_points = list(range(self._eval_frequency, total_rows + 1, self._eval_frequency))
        if eval_points[-1] != total_rows:
            eval_points.append(total_rows)

        results: list[ConvergenceResult] = []
        for point in eval_points:
            sliced_df = samples.df.head(point)
            sliced_samples = SampleFrame(
                df=sliced_df,
                target_col=samples.target_col,
                it_col=samples.it_col,
            )
            result = self._criterion.run(sliced_samples, params)
            results.append(result)

        data_frames = [r.data for r in results]
        combined_data = pl.concat(data_frames, how="align")

        final = results[-1]
        return ConvergenceResult(
            method=final.method,
            n=final.n,
            estimate=final.estimate,
            error=final.error,
            is_converged=final.is_converged,
            data=combined_data,
            diagnostics={
                **final.diagnostics,
                "eval_frequency": self._eval_frequency,
                "n_evaluations": len(results),
            },
        )
