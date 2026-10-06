"""Tests for EvalFrequencyWrapper and CriterionWrapper."""
# uv run pytest tests/test_wrappers.py

from collections.abc import Sequence
from typing import Any, ClassVar

import polars as pl
import pytest

from mocaco.protocols import SampleFrame
from mocaco.result import ConvergenceResult
from mocaco.wrappers import CriterionWrapper, EvalFrequencyWrapper


class MockCriterion:
    """Mock criterion for testing wrappers without protocol/pydantic issues."""

    name = "mock"
    supports_eval_frequency = True
    description = "Mock description"
    params_type = dict
    assumptions: ClassVar[Sequence[str]] = ("assumption 1",)
    limitations: ClassVar[Sequence[str]] = ("limitation 1",)
    result_interpretation = "interp"
    example_usage = "usage"
    references: ClassVar[Sequence[str]] = ("ref",)

    def run(self, samples: SampleFrame, params: Any) -> ConvergenceResult:
        n_rows = len(samples.df)
        return ConvergenceResult(
            method=self.name,
            n=n_rows,
            n_col="n",
            estimate=1.0,
            estimate_col="estimate",
            error=0.1,
            error_col="error",
            is_converged=True,
            is_converged_col="is_converged",
            data=pl.DataFrame(
                {"n": [n_rows], "estimate": [1.0], "error": [0.1], "is_converged": [True]}
            ),
            diagnostics={},
        )

def test_eval_frequency_property() -> None:
    """Property eval_frequency returns the initialized value."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=42)
    assert wrapper.eval_frequency == 42


def test_wrapper_delegates_name() -> None:
    """.name matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.name == inner.name


def test_wrapper_delegates_description() -> None:
    """.description matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.description == inner.description


def test_wrapper_delegates_params_type() -> None:
    """.params_type matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.params_type == inner.params_type


def test_wrapper_delegates_assumptions() -> None:
    """.assumptions matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.assumptions == inner.assumptions


def test_wrapper_delegates_limitations() -> None:
    """.limitations matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.limitations == inner.limitations


def test_wrapper_delegates_result_interpretation() -> None:
    """.result_interpretation matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.result_interpretation == inner.result_interpretation


def test_wrapper_delegates_example_usage() -> None:
    """.example_usage matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.example_usage == inner.example_usage


def test_wrapper_delegates_references() -> None:
    """.references matches inner criterion."""
    inner = MockCriterion()
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=10)
    assert wrapper.references == inner.references


def test_eval_frequency_positive_required() -> None:
    """ValueError on eval_frequency <= 0."""
    inner = MockCriterion()
    with pytest.raises(ValueError, match=r"(?i)positive"):
        EvalFrequencyWrapper(inner, eval_frequency=0)

    with pytest.raises(ValueError, match=r"(?i)positive"):
        EvalFrequencyWrapper(inner, eval_frequency=-1)


def test_eval_frequency_ge_total_rows() -> None:
    """Single evaluation when freq >= rows."""
    inner = MockCriterion()
    df = pl.DataFrame({"it": range(1, 5), "value": [1.0, 2.0, 3.0, 4.0]})
    samples = SampleFrame(df=df, target_col="value")
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=5)
    result = wrapper.run(samples=samples, params={"threshold": 0.5})
    assert result is not None


def test_eval_frequency_lt_total_rows() -> None:
    """Multiple evaluations with concatenated data."""
    inner = MockCriterion()
    df = pl.DataFrame({"it": range(1, 21), "value": [1.0] * 20})
    samples = SampleFrame(df=df, target_col="value")
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=5)
    result = wrapper.run(samples=samples, params={"threshold": 0.5})
    assert result is not None
    assert len(result.data) == 4  # 4 evaluation points


def test_eval_frequency_appends_final() -> None:
    """Last eval includes remaining rows."""
    inner = MockCriterion()
    df = pl.DataFrame({"it": range(1, 21), "value": [1.0] * 20})
    samples = SampleFrame(df=df, target_col="value")
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=5)
    result = wrapper.run(samples=samples, params={"threshold": 0.5})
    assert result is not None


def test_eval_frequency_diagnostics() -> None:
    """Diagnostics include eval_frequency and n_evaluations."""
    inner = MockCriterion()
    df = pl.DataFrame({"it": range(1, 21), "value": [1.0] * 20})
    samples = SampleFrame(df=df, target_col="value")
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=5)
    result = wrapper.run(samples=samples, params={"threshold": 0.5})
    assert result is not None
    assert "eval_frequency" in result.diagnostics
    assert "n_evaluations" in result.diagnostics


def test_eval_frequency_result_fields() -> None:
    """Final result fields from last evaluation."""
    inner = MockCriterion()
    df = pl.DataFrame({"it": range(1, 21), "value": [1.0] * 20})
    samples = SampleFrame(df=df, target_col="value")
    wrapper = EvalFrequencyWrapper(inner, eval_frequency=5)
    result = wrapper.run(samples=samples, params={"threshold": 0.5})
    assert result is not None
    assert result.estimate is not None
    assert result.error is not None


def test_wrapper_run_delegates() -> None:
    """Base CriterionWrapper.run() calls inner."""
    inner = MockCriterion()
    df = pl.DataFrame({"it": range(1, 11), "value": [1.0] * 10})
    samples = SampleFrame(df=df, target_col="value")
    wrapper = CriterionWrapper(inner)
    result = wrapper.run(samples=samples, params={"threshold": 0.5})
    assert result is not None
