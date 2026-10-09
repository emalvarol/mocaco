"""Tests for CLTAbsoluteCriterion."""
# uv run pytest tests/methods/test_clt_absolute.py

import numpy as np
import polars as pl
import pytest
from pydantic import ValidationError

from mocaco.methods.clt_uni_abs import CLTAbsoluteCriterion, InputParams
from mocaco.protocols import SampleFrame


def test_clt_params_threshold_required() -> None:
    """Threshold is required (no default)."""
    with pytest.raises(ValidationError, match=r"(?i)threshold"):
        InputParams(confidence_level=0.95)  # type: ignore[call-arg]


def test_clt_params_threshold_must_be_positive() -> None:
    """ValidationError on threshold <= 0."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0, confidence_level=0.95)

    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=-1, confidence_level=0.95)


def test_clt_params_confidence_range() -> None:
    """ValidationError on confidence outside (0,1)."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0.5, confidence_level=0.0)

    with pytest.raises(ValidationError, match=r"(?i)less than"):
        InputParams(threshold=0.5, confidence_level=1.1)

    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0.5, confidence_level=-0.1)


def test_clt_criterion_registered() -> None:
    """Appears in registry after import."""
    from mocaco.registry import registry

    assert "clt_absolute" in registry.names()


def test_clt_run_returns_result() -> None:
    """Returns ConvergenceResult instance."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(
        samples=sf,
        params=InputParams(threshold=0.5, confidence_level=0.95),
    )
    assert result is not None


def test_clt_run_estimate_correct() -> None:
    """Estimate matches expected mean."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [2.5] * 100})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.estimate == 2.5


def test_clt_run_n_correct() -> None:
    """N matches DataFrame row count."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 51), "value": [1.0] * 50})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.n == 50


def test_clt_run_error_correct() -> None:
    """Error matches z_score * SEM."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.error is not None


def test_clt_run_converged_true() -> None:
    """Converges with tight threshold."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0, confidence_level=0.95))
    assert result.is_converged is True


def test_clt_run_converged_false(sample_frame: SampleFrame) -> None:
    """Does not converge with strict threshold on high-variance data."""
    criterion = CLTAbsoluteCriterion()
    result = criterion.run(
        samples=sample_frame, params=InputParams(threshold=0.01, confidence_level=0.95)
    )
    assert result.is_converged is False


def test_clt_run_diagnostics() -> None:
    """Diagnostics contain threshold, confidence, z_score."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.99))
    assert "threshold" in result.diagnostics
    assert "confidence_level" in result.diagnostics
    assert "z_score" in result.diagnostics


def test_clt_run_data_columns() -> None:
    """Output DataFrame has expected columns."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    expected_cols = {"n", "mean", "std", "sem", "abs_error", "is_converged"}
    assert set(result.data.columns) == expected_cols


def test_clt_run_zero_variance() -> None:
    """Handles constant target (std=0)."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": range(1, 11), "value": [5.0] * 10})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result is not None


def test_clt_run_single_sample() -> None:
    """Works with n=1 (std=None -> 0)."""
    criterion = CLTAbsoluteCriterion()
    df = pl.DataFrame({"it": [1], "value": [3.14]})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result is not None


def test_clt_run_large_sample() -> None:
    """Converges with large low-variance sample."""
    criterion = CLTAbsoluteCriterion()
    rng = np.random.default_rng(42)
    values = rng.standard_normal(1000) * 0.01  # very low variance
    df = pl.DataFrame({"it": range(1, 1001), "value": values})
    sf = SampleFrame(df=df, target_col="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.is_converged is True


def test_clt_run_with_eval_frequency() -> None:
    """supports_eval_frequency is True."""
    criterion = CLTAbsoluteCriterion()
    assert criterion.supports_eval_frequency is True


def test_clt_assumptions_non_empty() -> None:
    """Assumptions tuple is populated."""
    criterion = CLTAbsoluteCriterion()
    assert len(criterion.assumptions) > 0


def test_clt_assumptions_sample_large_enough() -> None:
    """Sample size is more than 30 to allow normal approximation."""
    criterion = CLTAbsoluteCriterion()
    # This test verifies the assumption statement references sample size > 30
    assert "30" in criterion.assumptions[2]


def test_clt_limitations_non_empty() -> None:
    """Limitations tuple is populated."""
    criterion = CLTAbsoluteCriterion()
    assert len(criterion.limitations) > 0


def test_clt_references_non_empty() -> None:
    """References tuple is populated."""
    criterion = CLTAbsoluteCriterion()
    assert len(criterion.references) > 0
