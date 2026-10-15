"""Tests for CLTRelativeCriterion."""
# uv run pytest tests/methods/test_clt_uni_rel.py

import numpy as np
import polars as pl
import pytest
from pydantic import ValidationError
from scipy.stats import norm

from mocaco.methods.clt_uni_rel import CLTRelativeCriterion, InputParams
from mocaco.protocols import SampleFrame
from mocaco.result import ConvergenceResult, GroupedConvergenceResult


def _linear_frame(n: int = 100) -> pl.DataFrame:
    """Return an n-row DataFrame with linearly increasing values (mean n+1/2)."""
    return pl.DataFrame({"it": range(1, n + 1), "value": [float(i) for i in range(1, n + 1)]})


def test_clt_rel_params_threshold_required() -> None:
    """Threshold is required (no default)."""
    with pytest.raises(ValidationError, match=r"(?i)threshold"):
        InputParams(confidence_level=0.95)  # type: ignore[call-arg]


def test_clt_rel_params_threshold_must_be_positive() -> None:
    """ValidationError on threshold <= 0."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0, confidence_level=0.95)

    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=-1, confidence_level=0.95)


def test_clt_rel_params_confidence_range() -> None:
    """ValidationError on confidence outside (0,1)."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0.5, confidence_level=0.0)

    with pytest.raises(ValidationError, match=r"(?i)less than"):
        InputParams(threshold=0.5, confidence_level=1.1)


def test_clt_rel_criterion_registered() -> None:
    """Appears in registry after import."""
    from mocaco.registry import registry

    assert "clt_uni_rel" in registry.names()


def test_clt_rel_run_returns_result() -> None:
    """Returns ConvergenceResult instance."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(), target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert isinstance(result, ConvergenceResult)


def test_clt_rel_run_estimate_correct() -> None:
    """Estimate matches expected mean."""
    criterion = CLTRelativeCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [2.5] * 100})
    sf = SampleFrame(df=df, target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.estimate == 2.5


def test_clt_rel_run_n_correct() -> None:
    """N matches DataFrame row count."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(50), target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.n == 50


def test_clt_rel_run_error_correct() -> None:
    """Error matches abs_error / |mean|."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(100), target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))

    z_score = float(norm.ppf(1.0 - (1.0 - 0.95) / 2.0))
    std = float(np.std([float(i) for i in range(1, 101)], ddof=1))
    sem = std / (100**0.5)
    expected = (sem * z_score) / abs(50.5)
    assert result.error == pytest.approx(expected, rel=1e-9)


def test_clt_rel_run_error_col_is_rel_error() -> None:
    """The reported error column is the relative error."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(100), target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.error_col == "rel_error"


def test_clt_rel_run_converged_true() -> None:
    """Converges with a loose threshold on zero-variance data."""
    criterion = CLTRelativeCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sf = SampleFrame(df=df, target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0, confidence_level=0.95))
    assert result.is_converged is True


def test_clt_rel_run_converged_false(sample_frame: SampleFrame) -> None:
    """Does not converge with strict threshold on high-variance data."""
    criterion = CLTRelativeCriterion()
    result = criterion.run(
        samples=sample_frame, params=InputParams(threshold=0.001, confidence_level=0.95)
    )
    assert result.is_converged is False


def test_clt_rel_run_diagnostics() -> None:
    """Diagnostics contain threshold, confidence, z_score and relative_error_used."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(), target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.99))
    assert {"threshold", "confidence_level", "z_score", "relative_error_used"} <= set(
        result.diagnostics
    )


def test_clt_rel_run_data_columns() -> None:
    """Output DataFrame has expected columns."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(), target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    expected_cols = {"n", "mean", "std", "sem", "abs_error", "rel_error", "is_converged"}
    assert set(result.data.columns) == expected_cols


def test_clt_rel_run_zero_variance(sample_frame_constant: SampleFrame) -> None:
    """Handles constant target (std=0)."""
    criterion = CLTRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_constant, params=InputParams(threshold=0.5, confidence_level=0.95)
    )
    assert result.error == 0.0


def test_clt_rel_run_near_zero_mean_fallback() -> None:
    """Falls back to absolute error when the estimate is near zero."""
    criterion = CLTRelativeCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [-1.0, 1.0] * 50})
    sf = SampleFrame(df=df, target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0, confidence_level=0.95))
    assert result.diagnostics["relative_error_used"] is False


def test_clt_rel_run_near_zero_mean_error_is_abs_error() -> None:
    """Returned error equals the absolute error when falling back."""
    criterion = CLTRelativeCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [-1.0, 1.0] * 50})
    sf = SampleFrame(df=df, target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0, confidence_level=0.95))
    assert result.error == result.data["abs_error"][0]


def test_clt_rel_run_near_zero_mean_rel_error_is_null() -> None:
    """Relative error column is null when the estimate is near zero."""
    criterion = CLTRelativeCriterion()
    df = pl.DataFrame({"it": range(1, 101), "value": [-1.0, 1.0] * 50})
    sf = SampleFrame(df=df, target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0, confidence_level=0.95))
    assert result.data["rel_error"][0] is None


def test_clt_rel_run_large_sample() -> None:
    """Converges with large low-variance sample."""
    criterion = CLTRelativeCriterion()
    rng = np.random.default_rng(42)
    values = rng.standard_normal(1000) * 0.01 + 10.0
    df = pl.DataFrame({"it": range(1, 1001), "value": values})
    sf = SampleFrame(df=df, target_cols="value")
    result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.is_converged is True


def test_clt_rel_run_insufficient_sample_warns(sample_df_small: pl.DataFrame) -> None:
    """Warns when fewer than 30 samples are available."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=sample_df_small, target_cols="value")
    with pytest.warns(UserWarning, match="less than the required minimum of 30"):
        criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))


def test_clt_rel_run_insufficient_sample_not_converged(sample_df_small: pl.DataFrame) -> None:
    """The insufficient-sample warm-up path returns a not-converged result."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=sample_df_small, target_cols="value")
    with pytest.warns(UserWarning, match="less than the required minimum of 30"):
        result = criterion.run(samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95))
    assert result.is_converged is False


def test_clt_rel_run_with_eval_frequency() -> None:
    """eval_frequency produces a periodic diagnostic frame."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(100), target_cols="value")
    result = criterion.run(
        samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95, eval_frequency=10)
    )
    assert result.data.height <= 10


def test_clt_rel_run_eval_frequency_last_row_is_total() -> None:
    """The final evaluated row always corresponds to the full sample."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(100), target_cols="value")
    result = criterion.run(
        samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95, eval_frequency=10)
    )
    assert result.n == 100


def test_clt_rel_run_eval_frequency_diagnostics() -> None:
    """eval_frequency diagnostics report frequency and number of evaluations."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(100), target_cols="value")
    result = criterion.run(
        samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95, eval_frequency=10)
    )
    assert result.diagnostics["eval_frequency"] == 10


def test_clt_rel_run_eval_frequency_has_rel_error_column() -> None:
    """The eval_frequency frame still exposes the relative error column."""
    criterion = CLTRelativeCriterion()
    sf = SampleFrame(df=_linear_frame(100), target_cols="value")
    result = criterion.run(
        samples=sf, params=InputParams(threshold=0.5, confidence_level=0.95, eval_frequency=10)
    )
    assert "rel_error" in result.data.columns


def test_clt_rel_grouped_returns_grouped_result(sample_frame_grouped: SampleFrame) -> None:
    """Grouped input yields a GroupedConvergenceResult."""
    criterion = CLTRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_grouped, params=InputParams(threshold=0.5, confidence_level=0.95)
    )
    assert isinstance(result, GroupedConvergenceResult)


def test_clt_rel_grouped_keys(sample_frame_grouped: SampleFrame) -> None:
    """Grouped result keys map the group column to its values."""
    criterion = CLTRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_grouped, params=InputParams(threshold=0.5, confidence_level=0.95)
    )
    assert isinstance(result, dict)
    assert {dict(key)["group"] for key in result} == {"a", "b"}


def test_clt_rel_grouped_per_group_n(sample_frame_grouped: SampleFrame) -> None:
    """Each group reports its own sample count."""
    criterion = CLTRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_grouped, params=InputParams(threshold=0.5, confidence_level=0.95)
    )
    assert isinstance(result, dict)
    assert all(res.n == 40 for res in result.values())


def test_clt_rel_grouped_error_by(sample_frame_grouped: SampleFrame) -> None:
    """error_by keeps the requested group column."""
    criterion = CLTRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_grouped, params=InputParams(threshold=0.5, confidence_level=0.95)
    )
    assert set(result.error_by(keep="group")) == {(("group", "a"),), (("group", "b"),)}


def test_clt_assumptions_non_empty() -> None:
    """Assumptions tuple is populated."""
    criterion = CLTRelativeCriterion()
    assert len(criterion.assumptions) > 0


def test_clt_assumptions_sample_large_enough() -> None:
    """Sample size is more than 30 to allow normal approximation."""
    criterion = CLTRelativeCriterion()
    assert "30" in criterion.assumptions[2]


def test_clt_limitations_non_empty() -> None:
    """Limitations tuple is populated."""
    criterion = CLTRelativeCriterion()
    assert len(criterion.limitations) > 0


def test_clt_references_non_empty() -> None:
    """References tuple is populated."""
    criterion = CLTRelativeCriterion()
    assert len(criterion.references) > 0
