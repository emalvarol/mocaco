"""Tests for CLTMultivariateRelativeCriterion."""
# uv run pytest tests/methods/test_clt_multi_rel.py

import numpy as np
import polars as pl
import pytest
from pydantic import ValidationError

from mocaco.methods.clt_multi_rel import (
    CLTMultivariateRelativeCriterion,
    InputParams,
    _vats_components,
)
from mocaco.protocols import SampleFrame
from mocaco.result import ConvergenceResult, GroupedConvergenceResult


def _grouped_multi_frame(rows: int = 120) -> pl.DataFrame:
    """Two groups of ``rows`` rows each, with two target columns."""
    rng = np.random.default_rng(5)
    frames = [
        pl.DataFrame(
            {
                "group": [name] * rows,
                "it": list(range(1, rows + 1)),
                "a": rng.standard_normal(rows),
                "b": rng.standard_normal(rows),
            }
        )
        for name in ("a", "b")
    ]
    return pl.concat(frames)


def test_clt_multi_params_epsilon_must_be_positive() -> None:
    """ValidationError on epsilon <= 0."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(epsilon=0)


def test_clt_multi_params_alpha_range() -> None:
    """ValidationError on alpha outside (0,1)."""
    with pytest.raises(ValidationError, match=r"(?i)less than"):
        InputParams(epsilon=0.5, alpha=1.0)


def test_clt_multi_params_eval_frequency_positive() -> None:
    """ValidationError on non-positive eval_frequency."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(epsilon=0.5, eval_frequency=0)


def test_clt_multi_params_warm_up_period_positive() -> None:
    """ValidationError on non-positive warm_up_period."""
    with pytest.raises(ValidationError, match=r"(?i)greater than"):
        InputParams(epsilon=0.5, warm_up_period=0)


def test_clt_multi_params_warm_up_default() -> None:
    """warm_up_period defaults to 100."""
    assert InputParams(epsilon=0.5).warm_up_period == 100


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
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    assert result is not None


def test_clt_multi_run_converged_true(sample_frame_multi_target: SampleFrame) -> None:
    """Converges with a loose tolerance."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    assert result.is_converged is True


def test_clt_multi_run_converged_false(sample_frame_multi_target: SampleFrame) -> None:
    """Does not converge with a strict tolerance."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.05))
    assert result.is_converged is False


def test_clt_multi_run_n_matches_max_it(sample_frame_multi_target: SampleFrame) -> None:
    """N is the final checkpoint iteration."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    assert result.n == 300


def test_clt_multi_run_error_is_confidence_region_radius(
    sample_frame_multi_target: SampleFrame,
) -> None:
    """The reported error is the confidence-region radius (lhs) at the final checkpoint."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    matrix = sample_frame_multi_target.df.select(["a", "b"]).to_numpy()
    _, expected_error, _, _ = _vats_components(matrix, 0.05, 0.5)
    assert result.error == pytest.approx(expected_error)


def test_clt_multi_run_estimate_is_natural_scale(
    sample_frame_multi_target: SampleFrame,
) -> None:
    """The estimate is the natural scale det(cov)^(1/(2p)) at the final checkpoint."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    matrix = sample_frame_multi_target.df.select(["a", "b"]).to_numpy()
    expected_estimate, _, _, _ = _vats_components(matrix, 0.05, 0.5)
    assert result.estimate == pytest.approx(expected_estimate)


def test_clt_multi_run_threshold_diagnostic_is_rhs(
    sample_frame_multi_target: SampleFrame,
) -> None:
    """Diagnostics store the threshold rhs = epsilon * natural scale at the final checkpoint."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    matrix = sample_frame_multi_target.df.select(["a", "b"]).to_numpy()
    _, _, expected_threshold, _ = _vats_components(matrix, 0.05, 0.5)
    assert result.diagnostics["threshold"] == pytest.approx(expected_threshold)


def test_clt_multi_run_residual_error_is_gap(
    sample_frame_multi_target: SampleFrame,
) -> None:
    """residual_error is max(0, error - threshold)."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.05))

    assert isinstance(result, ConvergenceResult)
    expected = max(0.0, result.error - result.diagnostics["threshold"])
    assert result.residual_error == pytest.approx(expected)


def test_clt_multi_run_data_columns(sample_frame_multi_target: SampleFrame) -> None:
    """Output DataFrame has the expected columns."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    assert set(result.data.columns) == {"n", "estimate", "error", "non_conv_count", "is_converged"}


def test_clt_multi_run_diagnostics(sample_frame_multi_target: SampleFrame) -> None:
    """Diagnostics expose alpha, epsilon, threshold and dimensionality."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(samples=sample_frame_multi_target, params=InputParams(epsilon=0.5))
    assert result.diagnostics["epsilon"] == 0.5
    assert result.diagnostics["alpha"] == 0.05
    assert result.diagnostics["threshold"] > 0.0
    assert result.diagnostics["n_targets"] == 2
    assert "tolerance" not in result.diagnostics


def test_clt_multi_run_eval_frequency_history(sample_frame_multi_target: SampleFrame) -> None:
    """eval_frequency produces multiple checkpoints."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_multi_target,
        params=InputParams(epsilon=0.5, eval_frequency=50),
    )
    assert result.data.height > 1


def test_clt_multi_run_warm_up_period(sample_frame_multi_target: SampleFrame) -> None:
    """warm_up_period sets the first evaluated iteration."""
    criterion = CLTMultivariateRelativeCriterion()
    result = criterion.run(
        samples=sample_frame_multi_target,
        params=InputParams(epsilon=0.5, eval_frequency=50, warm_up_period=100),
    )
    assert result.data["n"][0] == 100


def test_clt_multi_run_warm_up_not_reached_warns() -> None:
    """A chain shorter than the warm-up warns and is forced to not converged."""
    criterion = CLTMultivariateRelativeCriterion()
    rng = np.random.default_rng(1)
    df = pl.DataFrame({"a": rng.standard_normal(10), "b": rng.standard_normal(10)})
    sf = SampleFrame(df=df, target_cols=["a", "b"])
    with pytest.warns(UserWarning, match="Warm-up period not reached"):
        result = criterion.run(samples=sf, params=InputParams(epsilon=0.5))
    assert result.is_converged is False


def test_clt_multi_run_constant_column_zero_error() -> None:
    """A constant column makes the covariance degenerate, so the error is 0."""
    criterion = CLTMultivariateRelativeCriterion()
    df = pl.DataFrame({"it": range(1, 101), "a": [float(i % 5) for i in range(100)], "b": [2.0] * 100})
    sf = SampleFrame(df=df, target_cols=["a", "b"])
    result = criterion.run(samples=sf, params=InputParams(epsilon=0.05))
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
    result = criterion.run(samples=sf, params=InputParams(epsilon=1.0))
    assert isinstance(result, GroupedConvergenceResult)


def test_clt_multi_grouped_keys() -> None:
    """Grouped result keys map the group column to its values."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(df=_grouped_multi_frame(), target_cols=["a", "b"], group_cols="group")
    result = criterion.run(samples=sf, params=InputParams(epsilon=1.0))
    assert isinstance(result, dict)
    assert {dict(key)["group"] for key in result} == {"a", "b"}


def test_clt_multi_grouped_per_group_n() -> None:
    """Each group reports its own final checkpoint."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(df=_grouped_multi_frame(), target_cols=["a", "b"], group_cols="group")
    result = criterion.run(samples=sf, params=InputParams(epsilon=1.0))
    assert isinstance(result, dict)
    assert all(res.n == 120 for res in result.values())


def test_clt_multi_grouped_residual_error_by() -> None:
    """residual_error_by keeps the requested group column."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(df=_grouped_multi_frame(), target_cols=["a", "b"], group_cols="group")
    result = criterion.run(samples=sf, params=InputParams(epsilon=1.0))
    assert set(result.residual_error_by(keep="group")) == {(("group", "a"),), (("group", "b"),)}


def test_clt_multi_grouped_data_residual_error_by() -> None:
    """data_residual_error_by aggregates over the group column."""
    criterion = CLTMultivariateRelativeCriterion()
    sf = SampleFrame(
        df=_grouped_multi_frame(),
        target_cols=["a", "b"],
        group_cols="group",
    )
    result = criterion.run(samples=sf, params=InputParams(epsilon=1.0, eval_frequency=20))
    df = result.data_residual_error_by(keep=["group"])
    assert "res_error" in df.columns
