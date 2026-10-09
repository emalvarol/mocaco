"""Integration tests for end-to-end flows."""
# uv run pytest tests/test_integration.py

import polars as pl

from mocaco import convergence, describe, methods, samples


def test_full_pipeline_clt_uni_abs() -> None:
    """Samples -> convergence -> result -> summary."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sample_frame = samples(df, target_col="value", it_col="it")
    result = convergence(samples=sample_frame, method="clt_uni_abs", threshold=0.5)
    assert result is not None


def test_full_pipeline_with_eval_frequency() -> None:
    """Full pipeline with eval_frequency wrapper."""
    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sample_frame = samples(df, target_col="value", it_col="it")
    result = convergence(
        samples=sample_frame, method="clt_uni_abs", threshold=0.5, eval_frequency=10
    )
    assert result is not None


def test_method_discovery_flow() -> None:
    """methods() -> describe() -> convergence()."""
    names = methods()
    assert isinstance(names, tuple)
    describe("clt_uni_abs")


def test_result_export_polars() -> None:
    """to_polars() returns valid DataFrame."""
    import polars as pl

    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sample_frame = samples(df, target_col="value", it_col="it")
    result = convergence(samples=sample_frame, method="clt_uni_abs", threshold=0.5)
    polars_df = result.to_polars()
    assert isinstance(polars_df, pl.DataFrame)


def test_result_export_pandas() -> None:
    """to_pandas() returns valid DataFrame."""
    import pandas as pd
    import polars as pl

    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sample_frame = samples(df, target_col="value", it_col="it")
    result = convergence(samples=sample_frame, method="clt_uni_abs", threshold=0.5)
    pandas_df = result.to_pandas()
    assert isinstance(pandas_df, pd.DataFrame)


def test_result_plotting_pipeline() -> None:
    """result.plot.evolution() produces axes."""
    import matplotlib.axes
    import matplotlib.pyplot as plt

    df = pl.DataFrame({"it": range(1, 101), "value": [1.0] * 100})
    sample_frame = samples(df, target_col="value", it_col="it")
    result = convergence(samples=sample_frame, method="clt_uni_abs", threshold=0.5)
    ax = result.plot.evolution(show=False)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close()
