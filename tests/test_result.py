"""Tests for ConvergenceResult and ResultPlotter."""
# uv run pytest tests/test_result.py

import polars as pl
import pytest

from mocaco.result import ConvergenceResult


def test_result_creation() -> None:
    """Valid ConvergenceResult construction."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    assert result.method == "test"


def test_result_frozen() -> None:
    """Immutability of dataclass."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    with pytest.raises(AttributeError, match=r"cannot assign to field"):
        result.method = "changed"  # type: ignore[misc]


def test_result_diagnostics_default() -> None:
    """Diagnostics defaults to empty dict."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    assert result.diagnostics == {}


def test_result_to_polars() -> None:
    """Returns the data DataFrame."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    assert result.to_polars() is not None


def test_result_to_pandas() -> None:
    """Returns pandas DataFrame."""
    import pandas as pd
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    df = result.to_pandas()
    assert isinstance(df, pd.DataFrame)


def test_result_str() -> None:
    """String representation contains method name."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    s = repr(result)
    assert "ConvergenceResult" in s


def test_result_repr() -> None:
    """Compact repr with key fields."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    r = repr(result)
    assert "ConvergenceResult" in r


def test_result_summary_converged(capsys) -> None:
    """summary() prints "Converged" (capsys)."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    result.summary()
    captured = capsys.readouterr()
    assert "Converged" in captured.out


def test_result_summary_not_converged(capsys) -> None:
    """summary() prints "Not Converged"."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=False,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [False]}),
    )
    result.summary()
    captured = capsys.readouterr()
    assert "Not Converged" in captured.out


def test_result_summary_with_diagnostics(capsys) -> None:
    """Diagnostics appear in summary."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
        diagnostics={"threshold": 0.05, "confidence": 0.95},
    )
    result.summary()
    captured = capsys.readouterr()
    assert "threshold" in captured.out


def test_result_summary_none_estimate() -> None:
    """Handles None estimate gracefully."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=None,
        estimate_col="mean",
        error=None,
        error_col="abs_error",
        is_converged=None,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [None], "abs_error": [None], "is_converged": [None]}),
    )
    s = str(result)
    assert "None" in s or "null" in s


def test_result_plotter_creation() -> None:
    """ResultPlotter instantiated via .plot."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [True]}),
    )
    plotter = result.plot
    assert plotter is not None


def test_plotter_evolution_returns_axes() -> None:
    """Returns matplotlib Axes."""
    import matplotlib.axes
    import matplotlib.pyplot as plt
    import polars as pl

    from mocaco.result import ConvergenceResult

    plt.switch_backend("Agg")

    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame(
            {
                "n": list(range(1, 101)),
                "mean": [3.14] * 100,
                "abs_error": [0.1] * 100,
                "is_converged": [True] * 100,
            }
        ),
    )

    ax = result.plot.evolution()
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close()


def test_plotter_evolution_missing_cols_raises() -> None:
    """ValueError when required columns missing."""
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"other": [1]}),
    )
    with pytest.raises(ValueError, match=r"(?i)missing|column"):
        result.plot.evolution()


def test_plotter_evolution_no_convergence() -> None:
    """Plot works when is_converged all False."""
    import matplotlib.pyplot as plt
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=False,
        is_converged_col="is_converged",
        data=pl.DataFrame(
            {
                "n": list(range(1, 101)),
                "mean": [3.14] * 100,
                "abs_error": [0.1] * 100,
                "is_converged": [False] * 100,
            }
        ),
    )
    ax = result.plot.evolution()
    import matplotlib.axes
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close()


def test_plotter_evolution_with_show_false() -> None:
    """Does not call plt.show() when show=False."""
    import matplotlib.pyplot as plt
    result = ConvergenceResult(
        method="test",
        n=100,
        n_col="n",
        estimate=3.14,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame(
            {
                "n": list(range(1, 101)),
                "mean": [3.14] * 100,
                "abs_error": [0.1] * 100,
                "is_converged": [True] * 100,
            }
        ),
    )
    # This should not show the plot, just return axes
    ax = result.plot.evolution(show=False)
    import matplotlib.axes
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close()
