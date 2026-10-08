"""Test."""
# uv run pytest benchmarks/ --benchmark-columns=min,mean,stddev,median,ops --benchmark-sort=mean
# uv run pytest benchmarks/ --benchmark-histogram=benchmarks/plots/histogram
import numpy as np
import polars as pl
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

import mocaco as mcc
from mocaco.protocols import SampleFrame


def generate_samples(n_rows: int) -> SampleFrame:
    """Genera datos sintéticos para las pruebas de rendimiento."""
    rng = np.random.default_rng(42)
    df = pl.DataFrame(
        {
            "it": range(1, n_rows + 1),
            "val": rng.normal(loc=10.0, scale=2.0, size=n_rows),
        }
    )
    return mcc.samples(df, target_col="val", it_col="it")


@pytest.mark.benchmark(group="eval_frequency_comparison")
@pytest.mark.parametrize("n_samples", [10_000, 100_000, 1_000_000])
@pytest.mark.parametrize("eval_freq", [100, 1_000, 10_000])
@pytest.mark.parametrize("implementation", ["native", "wrapper"])
def test_bench_eval_frequency_scaling(
    benchmark: BenchmarkFixture,
    n_samples: int,
    eval_freq: int,
    implementation: str,
) -> None:
    """Evalúa el tiempo de ejecución según el tamaño y la frecuencia de evaluación."""
    samples = generate_samples(n_samples)

    if implementation == "native":
        res = benchmark(
            mcc.convergence.clt_absolute,
            samples,
            threshold=0.01,
            eval_frequency=eval_freq,
        )
    else:
        res = benchmark(
            mcc.convergence.clt_uni_abs,  # type: ignore
            samples,
            threshold=0.01,
            eval_frequency=eval_freq,
        )

    assert res.data is not None
