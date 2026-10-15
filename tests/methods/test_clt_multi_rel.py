"""Tests for CLTMultivariateRelativeCriterion."""
# uv run pytest tests/methods/test_clt_multi_rel.py

import numpy as np
import polars as pl
import pytest
from pydantic import ValidationError

from mocaco.methods.clt_multi_rel import (
    CLTMultivariateRelativeCriterion,
    InputParams,
    _relative_residual,
)
from mocaco.protocols import SampleFrame
from mocaco.result import GroupedConvergenceResult


def _grouped_multi_frame() -> pl.DataFrame:
    """120-row DataFrame with two groups of 60 rows and two target columns."""
    rng = np.random.default_rng(5)
    frames = [
        pl.DataFrame(
            {
                "group": [name] * 60,
                "it": list(range(1, 61)),
                "a": rng.standard_normal(60),
                "b": rng.standard_normal(60),
            }
        )
        for name in ("a", "b")
    ]
    return pl.concat(frames)


def test_clt_multi_params_threshold_required() -> None:
    """Threshold is required (no default)."""
    with pytest.raises(ValidationError, match=r"(?i)threshold"):
        InputParams(confidence_level=0.95)  # type: ignore[call-arg]


def test_clt_multi_params_threshold_must_be_positive() -> None:
    """ValidationError on threshold <= 0."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0)


def test_clt_multi_params_confidence_range() -> None:
    """ValidationError on confidence outside (0,1)."""
    with pytest.raises(ValidationError, match=r"(?i)less than"):
        InputParams(threshold=0.5, confidence_level=1.0)


def test_clt_multi_params_eval_frequency_positive() -> None:
    """ValidationError on non-positive eval_frequency."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0.5, eval_frequency=0)


def test_clt_multi_params_first_check_point_positive() -> None:
    """ValidationError on non-positive first_check_point."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(threshold=0.5, first_check_point=0)


def test_clt_multi_criterion_registered() -> None:
    """Appears in registry after import."""
    from mocaco.registry import registry

    assert "clt_multi_rel" in registry.names()


def test_clt_multi_dimensionality() -> None:
    """Criterion declares itself multivariate."""
    assert CLTMultivariateRelativeCriterion.dimensionality == "multivariate"


def test_clt_multi_run_returns_result(sample_frame_multi_target: SampleFrame) -> None:
    """Returns a result object."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.5))
    assert result is not None


def test_clt_multi_run_converged_true(sample_frame_multi_target: SampleFrame) -> None:
    """Converges with a loose tolerance."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.5))
    assert result.is_converged is True


def test_clt_multi_run_converged_false(sample_frame_multi_target: SampleFrame) -> None:
    """Does not converge with a strict tolerance."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.05))
    assert result.is_converged is False


def test_clt_multi_run_n_matches_max_it(sample_frame_multi_target: SampleFrame) -> None:
    """n is the final checkpoint iteration."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.5))
    assert result.n == 300


def test_clt_multi_run_error_matches_direct_computation(
    sample_frame_multi_target: SampleFrame,
) -> None:
    """The reported error matches the numpy residual core."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.5))
    matrix = sample_frame_multi_target.df.select(["a", "b"]).to_numpy()
    expected = _relative_residual(matrix, 0.05, 0.5)
    assert result.error == pytest.approx(expected)


def test_clt_multi_run_residual_error_equals_error(
    sample_frame_multi_target: SampleFrame,
) -> None:
    """residual_error equals the residual (threshold is net of the tolerance)."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.5))
    assert result.residual_error == result.error


def test_clt_multi_run_data_columns(sample_frame_multi_target: SampleFrame) -> None:
    """Output DataFrame has the expected columns."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.5))
    assert set(result.data.columns) == {"n", "residual", "non_conv_count", "is_converged"}


def test_clt_multi_run_diagnostics(sample_frame_multi_target: SampleFrame) -> None:
    """Diagnostics expose tolerance, threshold, dimensionality."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(threshold=0.5))
    assert result.diagnostics["tolerance"] == 0.5
    assert result.diagnostics["threshold"] == 0.0
    assert result.diagnostics["n_targets"] == 2


def test_clt_multi_run_eval_frequency_history(sample_frame_multi_target: SampleFrame) -> None:
    """eval_frequency produces multiple checkpoints."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_multi_target,
        params=InputParams(threshold=0.5, eval_frequency=50),
    )
    assert result.data.height > 1


def test_clt_multi_run_first_check_point(sample_frame_multi_target: SampleFrame) -> None:
    """first_check_point sets the first evaluated iteration."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_multi_target,
        params=InputParams(threshold=0.5, eval_frequency=50, first_check_point=100),
    )
    assert result.data["n"][0] == 100


def test_clt_multi_run_warmup_warns() -> None:
    """Warns when fewer than 30 samples are available."""
    criterion = CLTMultivariateRelativeCriterion()
    rng = np.random.default_rng(1)
    df = pl.DataFrame({"a": rng.standard_normal(10), "b": rng.standard_normal(10)})
    sf = SampleFrame(df=df, target_cols=["a", "b"])
    with pytest.warns(UserWarning, match="less than the required minimum of 30"):
        criterion.run(samples=sf, params=InputParams(threshold=0.5))


def test_clt_multi_run_warmup_not_converged() -> None:
    """The warm-up path returns a not-converged result."""
    criterion = CLTMultivariateRelativeCriterion()
    rng = np.random.default_rng(1)
    df = pl.DataFrame({"a": rng.standard_normal(10), "b": rng.standard_normal(10)})
    sf = SampleFrame(df=df, target_cols=["a", "b"])
    with pytest.warns(UserWarning, match="less than the required minimum of 30"):
        result = criterion.run(samples=sf, params=InputParams(threshold=0.5))
    assert result.is_converged is False


def test_clt_multi_run_constant_column_zero_residual() -> None:
    """A constant column makes the covariance degenerate, so the residual is 0."""
    criterion = CLTMultivariateRelativeCriterion()
    df = pl.DataFrame({"it": range(1, 41), "a": [float(i % 5) for i in range(40)], "b": [2.0] * 40})
    sf = SampleFrame(df=df, target_cols=["a", "b"])
    result = criterion.run(samples=sf, params=InputParams(threshold=0.05))
    assert result.error == 0.0


def test_clt_multi_assumptions_non_empty() -> None:
    """Assumptions tuple is populated."""
    criterion = CLTMultivariateRelativeCriterion()
    assert len(criterion.assumptions) > 0


def test_clt_multi_limitations_non_empty() -> None:
    """Limitations tuple is populated."""
    criterion = CLTMultivariateRelativeCriterion()
    assert len(criterion.limitations) > 0


def test_clt_multi_references_non_empty() -> None:
    """References tuple mentions Vats et al. (2019)."""
    criterion = CLTMultivariateRelativeCriterion()
    assert any("Vats" in ref for ref in criterion.references)


def test_clt_multi_grouped_returns_grouped_result() -> None:
    """Grouped input yields a GroupedConvergenceResult."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(df=_grouped_multi_frame(), target_cols=["a", "b"], group_cols="group")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0))
    assert isinstance(result, GroupedConvergenceResult)


def test_clt_multi_grouped_keys() -> None:
    """Grouped result keys map the group column to its values."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(df=_grouped_multi_frame(), target_cols=["a", "b"], group_cols="group")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0))
    assert isinstance(result, dict)
    assert {dict(key)["group"] for key in result} == {"a", "b"}


def test_clt_multi_grouped_per_group_n() -> None:
    """Each group reports its own final checkpoint."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(df=_grouped_multi_frame(), target_cols=["a", "b"], group_cols="group")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0))
    assert isinstance(result, dict)
    assert all(res.n == 60 for res in result.values())


def test_clt_multi_grouped_residual_error_by() -> None:
    """residual_error_by keeps the requested group column."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(df=_grouped_multi_frame(), target_cols=["a", "b"], group_cols="group")
    result = criterion.run(samples=sf, params=InputParams(threshold=1.0))
    assert set(result.residual_error_by(keep="group")) == {(("group", "a"),), (("group", "b"),)}


def test_clt_multi_grouped_data_residual_error_by() -> None:
    """data_residual_error_by aggregates over the group column."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(
        df=_grouped_multi_frame(),
        target_cols=["a", "b"],
        group_cols="group",
    )
    result = criterion.run(
        samples=sf, params=InputParams(threshold=1.0, eval_frequency=20)
    )
    df = result.data_residual_error_by(keep=["group"])
    assert "res_error" in df.columns
