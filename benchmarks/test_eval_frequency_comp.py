"""Test."""

# uv run pytest benchmarks/ --benchmark-json=benchmarks/results.json
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


def generate_grouped_samples(n_rows_per_group: int, n_groups: int) -> SampleFrame:
    """Genera datos sintéticos agrupados para las pruebas de rendimiento con group_cols."""
    rng = np.random.default_rng(42)
    n_rows = n_rows_per_group * n_groups
    df = pl.DataFrame(
        {
            "group": [f"g{i}" for i in range(n_groups) for _ in range(n_rows_per_group)],
            "it": list(range(1, n_rows_per_group + 1)) * n_groups,
            "val": rng.normal(loc=10.0, scale=2.0, size=n_rows),
        }
    )
    return mcc.samples(df, target_col="val", it_col="it", group_cols="group")


@pytest.mark.parametrize("n_samples", [100, 1_000, 10_000])
@pytest.mark.parametrize("eval_freq", [1, 10, 100])
@pytest.mark.parametrize("implementation", ["native", "native2"])
def test_bench_eval_frequency_scaling(
    benchmark: BenchmarkFixture,
    n_samples: int,
    eval_freq: int,
    implementation: str,
) -> None:
    """Evalúa el tiempo de ejecución según el tamaño y la frecuencia de evaluación."""
    benchmark.group = f"N={n_samples} | freq={eval_freq}"
    benchmark.name = implementation
    samples = generate_samples(n_samples)

    if implementation == "native":
        res = benchmark(
            mcc.convergence.clt_uni_abs,  # type: ignore
            samples,
            threshold=0.01,
            eval_frequency=eval_freq,
        )
    else:
        res = benchmark(
            mcc.convergence.clt_uni_abs2,  # type: ignore
            samples,
            threshold=0.01,
            eval_frequency=eval_freq,
        )

    assert res.data is not None


@pytest.mark.parametrize("n_groups", [1, 10, 100])
@pytest.mark.parametrize("method", ["clt_uni_abs", "clt_uni_rel"])
def test_bench_grouped_scaling(
    benchmark: BenchmarkFixture,
    n_groups: int,
    method: str,
) -> None:
    """Evalúa el tiempo de ejecución según el número de grupos (group_cols)."""
    benchmark.group = f"grouped | groups={n_groups}"
    benchmark.name = method
    samples = generate_grouped_samples(n_rows_per_group=100, n_groups=n_groups)

    criterion = getattr(mcc.convergence, method)
    res = benchmark(criterion, samples, threshold=0.01, eval_frequency=10)

    assert res.data is not None
