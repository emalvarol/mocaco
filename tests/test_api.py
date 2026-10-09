"""Tests for the Convergence API facade."""
# uv run pytest tests/test_api.py

from __future__ import annotations

import polars as pl
import pytest

import mocaco as mcc
from mocaco import convergence, describe, methods, samples
from mocaco.protocols import SampleFrame


def test_convergence_eval_frequency_in_diagnostics() -> None:
    """Eval frequency wrapper injects the frequency value into diagnostics."""
    df = pl.DataFrame({"it": range(1, 21), "value": [1.0] * 20})
    result = convergence(
        samples(df, target_col="value"), method="clt_uni_abs", threshold=0.5, eval_frequency=5
    )
    assert result.diagnostics.get("eval_frequency") == 5


def test_convergence_eval_frequency_count() -> None:
    """Eval frequency wrapper tracks the correct total number of evaluations."""
    df = pl.DataFrame({"it": range(1, 21), "value": [1.0] * 20})
    result = convergence(
        samples(df, target_col="value"), method="clt_uni_abs", threshold=0.5, eval_frequency=5
    )
    assert result.diagnostics.get("n_evaluations") == 4


def test_convergence_eval_frequency_data_length() -> None:
    """Eval frequency wrapper concatenates data matching the evaluation count."""
    df = pl.DataFrame({"it": range(1, 21), "value": [1.0] * 20})
    result = convergence(
        samples(df, target_col="value"), method="clt_uni_abs", threshold=0.5, eval_frequency=5
    )
    assert len(result.data) == 4


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
    assert sf.target_col == "value"
