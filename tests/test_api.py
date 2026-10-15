"""Tests for the Convergence API facade."""
# uv run pytest tests/test_api.py

from __future__ import annotations

import polars as pl
import pytest

import mocaco as mcc
from mocaco import convergence, describe, methods
from mocaco.protocols import SampleFrame
from mocaco.result import GroupedConvergenceResult


def test_convergence_call_with_method() -> None:
    """convergence(samples, method="clt_uni_abs")."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    samples = mcc.samples(df, target_col="value", it_col="it")
    result = convergence(samples=samples, method="clt_uni_abs", threshold=0.5)
    assert result is not None


def test_convergence_call_unknown_method_raises() -> None:
    """ValueError for unregistered method."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    samples = mcc.samples(df, target_col="value", it_col="it")
    with pytest.raises(ValueError, match="Unknown convergence criterion: 'nonexistent'"):
        convergence(samples=samples, method="nonexistent", threshold=0.5)


def test_convergence_getattr_dispatch() -> None:
    """convergence.clt_uni_abs(samples)."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    samples = mcc.samples(df, target_col="value", it_col="it")
    result = convergence.clt_uni_abs(samples, threshold=0.5)  # type: ignore[arg-type]
    assert result is not None


def test_convergence_getattr_unknown_raises() -> None:
    """ValueError for unknown attribute."""
    with pytest.raises(ValueError, match="Unknown convergence criterion: 'nonexistent'"):
        _ = convergence.nonexistent  # type: ignore[attr-defined]


def test_convergence_with_eval_frequency() -> None:
    """eval_frequency kwarg triggers wrapper."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    samples = mcc.samples(df, target_col="value", it_col="it")
    result = convergence(samples=samples, method="clt_uni_abs", threshold=0.5, eval_frequency=10)
    assert result is not None


def test_convergence_eval_frequency_unsupported_raises() -> None:
    """TypeError when criterion does not support eval_frequency."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    samples = mcc.samples(df, target_col="value", it_col="it")
    result = convergence(samples=samples, method="clt_uni_abs", threshold=0.5, eval_frequency=5)
    assert result is not None


def test_convergence_params_passed_through() -> None:
    """Kwargs become params model fields."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    samples = mcc.samples(df, target_col="value", it_col="it")
    result = convergence(
        samples=samples, method="clt_uni_abs", threshold=0.1, confidence_level=0.99
    )
    assert result is not None


def test_methods_returns_registered() -> None:
    """mcc.methods() returns expected names."""
    names = methods()
    assert isinstance(names, tuple)
    assert "clt_uni_abs" in names


def test_describe_existing_method() -> None:
    """mcc.describe("clt_uni_abs") prints info."""
    describe("clt_uni_abs")


def test_describe_unknown_method(capsys: pytest.CaptureFixture[str]) -> None:
    """describe() prints an error message for unknown method."""
    from mocaco import describe

    describe("nonexistent_method")
    captured = capsys.readouterr()
    assert "Error:" in captured.out


def test_samples_returns_sample_frame() -> None:
    """mcc.samples() returns SampleFrame."""
    df = pl.DataFrame({"it": range(1, 11), "value": [1.0] * 10})
    sf = mcc.samples(df, target_col="value")
    assert isinstance(sf, SampleFrame)


def test_samples_passes_columns() -> None:
    """target_col and it_col forwarded correctly."""
    df = pl.DataFrame({"it": range(1, 11), "value": [1.0] * 10})
    sf = mcc.samples(df, target_col="value", it_col="it")
    assert sf.it_col == "it"
    assert sf.target_cols == ["value"]


def test_samples_target_col_accepts_list() -> None:
    """A list of target columns is forwarded and normalized."""
    df = pl.DataFrame({"a": [1.0] * 10, "b": [2.0] * 10})
    sf = mcc.samples(df, target_col=["a", "b"])
    assert sf.target_cols == ["a", "b"]


def test_convergence_univariate_rejects_multiple_targets() -> None:
    """ValueError when a univariate method receives more than one target."""
    df = pl.DataFrame({"a": [1.0] * 100, "b": [2.0] * 100})
    samples = mcc.samples(df, target_col=["a", "b"])
    with pytest.raises(ValueError, match=r"(?i)univariate"):
        convergence(samples=samples, method="clt_uni_abs", threshold=0.5)


def test_convergence_multivariate_rejects_single_target() -> None:
    """ValueError when a multivariate method receives a single target."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    samples = mcc.samples(df, target_col="value", it_col="it")
    with pytest.raises(ValueError, match=r"(?i)multivariate"):
        convergence(samples=samples, method="clt_multi_rel", threshold=0.5)


def test_samples_passes_group_cols(sample_df_grouped: pl.DataFrame) -> None:
    """group_cols is forwarded to the SampleFrame."""
    sf = mcc.samples(sample_df_grouped, target_col="value", group_cols="group")
    assert sf.group_cols == ["group"]


def test_convergence_grouped_returns_grouped_result(sample_frame_grouped: SampleFrame) -> None:
    """Grouped samples produce a GroupedConvergenceResult."""
    result = convergence(samples=sample_frame_grouped, method="clt_uni_abs", threshold=0.5)
    assert isinstance(result, GroupedConvergenceResult)


def test_convergence_grouped_execution_time_set(sample_frame_grouped: SampleFrame) -> None:
    """Execution time is recorded for every group."""
    result = convergence(samples=sample_frame_grouped, method="clt_uni_abs", threshold=0.5)
    assert isinstance(result, GroupedConvergenceResult)
    assert all(res.execution_time_sec is not None for res in result.values())
