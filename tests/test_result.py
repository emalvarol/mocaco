"""Tests for ConvergenceResult and ResultPlotter."""
# uv run pytest tests/test_result.py

from dataclasses import replace

import polars as pl
import pytest

from mocaco.result import ConvergenceResult, GroupedConvergenceResult, ResultPlotter


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
        data=pl.DataFrame(
            {"n": [100], "mean": [3.14], "abs_error": [0.1], "is_converged": [False]}
        ),
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
        data=pl.DataFrame(
            {"n": [100], "mean": [None], "abs_error": [None], "is_converged": [None]}
        ),
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


def test_convergence_result_getitem_raises() -> None:
    """Ungrouped results are not subscriptable."""
    result = ConvergenceResult(
        method="test",
        n=1,
        n_col="n",
        estimate=1.0,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [1]}),
    )
    with pytest.raises(TypeError, match=r"(?i)not subscriptable"):
        _ = result[("group", "a")]


def test_convergence_result_error_by_raises() -> None:
    """Ungrouped results do not support error_by."""
    result = ConvergenceResult(
        method="test",
        n=1,
        n_col="n",
        estimate=1.0,
        estimate_col="mean",
        error=0.1,
        error_col="abs_error",
        is_converged=True,
        is_converged_col="is_converged",
        data=pl.DataFrame({"n": [1]}),
    )
    with pytest.raises(TypeError, match=r"(?i)without grouping"):
        result.error_by(keep="group")


def test_grouped_result_is_dict(grouped_result: GroupedConvergenceResult) -> None:
    """GroupedConvergenceResult is a dict of group keys."""
    assert isinstance(grouped_result, dict)


def test_grouped_result_len(grouped_result: GroupedConvergenceResult) -> None:
    """Two groups are present."""
    assert len(grouped_result) == 2


def test_grouped_result_n_sum(grouped_result: GroupedConvergenceResult) -> None:
    """N aggregates the sample counts of every group."""
    assert grouped_result.n == 100


def test_grouped_result_error_sum(grouped_result: GroupedConvergenceResult) -> None:
    """Error is the residual absolute sum across groups."""
    assert grouped_result.error == pytest.approx(0.3)


def test_grouped_result_error_none_when_all_none(
    make_convergence_result,
) -> None:
    """Error is None when no group exposes an error."""
    result = GroupedConvergenceResult(
        {
            (("group", "a"),): make_convergence_result(error=None),
            (("group", "b"),): make_convergence_result(error=None),
        }
    )
    assert result.error is None


def test_grouped_result_error_by_single(grouped_result: GroupedConvergenceResult) -> None:
    """error_by keeps a single group column."""
    assert grouped_result.error_by(keep="group") == {
        (("group", "a"),): pytest.approx(0.1),
        (("group", "b"),): pytest.approx(0.2),
    }


def test_grouped_result_error_by_list(grouped_result: GroupedConvergenceResult) -> None:
    """error_by accepts a list of group columns."""
    assert set(grouped_result.error_by(keep=["group"])) == {
        (("group", "a"),),
        (("group", "b"),),
    }


def test_grouped_result_error_by_unknown_raises(
    grouped_result: GroupedConvergenceResult,
) -> None:
    """error_by raises for unknown group columns."""
    with pytest.raises(ValueError, match=r"(?i)unknown group column"):
        grouped_result.error_by(keep="missing")


def test_grouped_result_error_by_collapses(make_convergence_result) -> None:
    """error_by marginalizes over group columns not kept."""
    result = GroupedConvergenceResult(
        {
            (("cat1", "A"), ("cat2", "X")): make_convergence_result(error=0.1),
            (("cat1", "A"), ("cat2", "Y")): make_convergence_result(error=0.2),
            (("cat1", "B"), ("cat2", "X")): make_convergence_result(error=0.4),
        }
    )
    assert result.error_by(keep=["cat1"]) == {
        (("cat1", "A"),): pytest.approx(0.3),
        (("cat1", "B"),): pytest.approx(0.4),
    }


def test_grouped_result_error_by_none_bucket(make_convergence_result) -> None:
    """A collapsed bucket with no errors maps to None."""
    result = GroupedConvergenceResult(
        {
            (("cat1", "A"), ("cat2", "X")): make_convergence_result(error=None),
            (("cat1", "B"), ("cat2", "X")): make_convergence_result(error=0.4),
        }
    )
    assert result.error_by(keep=["cat1"])[("cat1", "A"),] is None


def test_grouped_result_estimate_raises(grouped_result: GroupedConvergenceResult) -> None:
    """Estimate cannot be aggregated across groups."""
    with pytest.raises(TypeError, match=r"(?i)index a specific group"):
        _ = grouped_result.estimate


def test_grouped_result_diagnostics_raises(grouped_result: GroupedConvergenceResult) -> None:
    """Diagnostics cannot be aggregated across groups."""
    with pytest.raises(TypeError, match=r"(?i)index a specific group"):
        _ = grouped_result.diagnostics


def test_grouped_result_is_converged_all_true(grouped_result: GroupedConvergenceResult) -> None:
    """is_converged is True when every group converged."""
    assert grouped_result.is_converged is True


def test_grouped_result_is_converged_false_if_any(make_convergence_result) -> None:
    """is_converged is False when any group did not converge."""
    result = GroupedConvergenceResult(
        {
            (("group", "a"),): make_convergence_result(is_converged=True),
            (("group", "b"),): make_convergence_result(is_converged=False),
        }
    )
    assert result.is_converged is False


def test_grouped_result_data_has_group_column(grouped_result: GroupedConvergenceResult) -> None:
    """Combined data attaches the group columns."""
    assert "group" in grouped_result.data.columns


def test_grouped_result_data_row_count(grouped_result: GroupedConvergenceResult) -> None:
    """Combined data concatenates one row per group."""
    assert grouped_result.data.height == 2


def test_grouped_result_to_polars(grouped_result: GroupedConvergenceResult) -> None:
    """to_polars returns a Polars DataFrame."""
    assert isinstance(grouped_result.to_polars(), pl.DataFrame)


def test_grouped_result_to_pandas(grouped_result: GroupedConvergenceResult) -> None:
    """to_pandas returns a pandas DataFrame."""
    import pandas as pd

    assert isinstance(grouped_result.to_pandas(), pd.DataFrame)


def test_grouped_result_execution_time_none(grouped_result: GroupedConvergenceResult) -> None:
    """execution_time_sec is None when unset on every group."""
    assert grouped_result.execution_time_sec is None


def test_grouped_result_execution_time_sum(make_convergence_result) -> None:
    """execution_time_sec sums the per-group timings."""
    result = GroupedConvergenceResult(
        {
            (("group", "a"),): replace(make_convergence_result(), execution_time_sec=0.1),
            (("group", "b"),): replace(make_convergence_result(), execution_time_sec=0.2),
        }
    )
    assert result.execution_time_sec == pytest.approx(0.3)


def test_grouped_result_plotter_creation(grouped_result: GroupedConvergenceResult) -> None:
    """Plot returns a ResultPlotter."""
    assert isinstance(grouped_result.plot, ResultPlotter)


def test_grouped_result_plotter_evolution_raises(grouped_result: GroupedConvergenceResult) -> None:
    """Direct evolution plotting on a grouped result raises TypeError."""
    with pytest.raises(TypeError, match=r"(?i)not supported"):
        grouped_result.plot.evolution()


def test_grouped_result_summary_prints_groups(
    grouped_result: GroupedConvergenceResult, capsys
) -> None:
    """Summary prints one block per group."""
    grouped_result.summary()
    captured = capsys.readouterr()
    assert "group=a" in captured.out
