from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from . import methods as _methods  # noqa: F401
from .protocols import SampleFrame
from .registry import registry
from .wrappers import EvalFrequencyWrapper

if TYPE_CHECKING:
    import polars as pl

    from .result import ConvergenceResult


def samples(
    df: pl.DataFrame,
    *,
    target_col: str,
    it_col: Optional[str] = None,
) -> SampleFrame:
    """
    Create the normalized and frozen data representation used by convergence criteria.
    This prevents input errors and ensure the input data is read-only and is
    never modified accidentally.

    Parameters
        ----------
        df
            Source Polars DataFrame.
        it_col
            Column containing the iteration/order of the samples. If the user omit it, it
            is automatically completed.
        target_col
            Column containing the quantity to analyze.
    """
    return SampleFrame(
        df=df,
        target_col=target_col,
        it_col=it_col,
    )


class Convergence:
    """
    Callable namespace exposing registered convergence criteria as attributes.

    Use as ``convergence(samples, method="...", **kwargs)`` for generic calls,
    or ``convergence.clt_absolute(samples, threshold=...)`` for typed calls.
    """
    
    def __call__(
        self,
        samples: SampleFrame,
        *,
        method: str,
        **kwargs,
    ) -> ConvergenceResult:
        """Generic invocation using any registered criterion by name."""
        criterion = registry.get(method)
        eval_frequency = kwargs.pop("eval_frequency", None)
        params = criterion.params_type(**kwargs)

        if eval_frequency is not None:
            if not getattr(criterion, "supports_eval_frequency", False):
                raise TypeError(
                    f"Criterion '{criterion.name}' does not support eval_frequency"
                )
            wrapper = EvalFrequencyWrapper(criterion, eval_frequency=eval_frequency)
            return wrapper.run(samples=samples, params=params)

        return criterion.run(
            samples=samples,
            params=params,
        )

    def __getattr__(self, name: str):
        """Resolve registered criteria as callable attributes."""
        criterion = registry.get(name)

        def _method(samples: SampleFrame, **kwargs):
            eval_frequency = kwargs.pop("eval_frequency", None)
            params = criterion.params_type(**kwargs)

            if eval_frequency is not None:
                if not getattr(criterion, "supports_eval_frequency", False):
                    raise TypeError(
                        f"Criterion '{criterion.name}' does not support eval_frequency"
                    )
                wrapper = EvalFrequencyWrapper(criterion, eval_frequency=eval_frequency)
                return wrapper.run(samples=samples, params=params)

            return criterion.run(samples=samples, params=params)

        return _method


convergence = Convergence()


def methods() -> tuple[str, ...]:
    """Return the names of all registered convergence criteria."""
    return registry.names()


def describe(name: str) -> dict | None:
    """Return metadata and parameter information for a criterion."""
    return registry.describe(name)
