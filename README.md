# mocaco

[![CI/CD & Tests](https://github.com/emalvarol/mocaco/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/emalvarol/mocaco/actions/workflows/ci-cd.yml)
![PyPi Version](https://img.shields.io/github/v/tag/emalvarol/mocaco?sort=semver&filter=v*.*.*&label=version)
![Python Versions](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue)
[![codecov](https://codecov.io/gh/emalvarol/mocaco/graph/badge.svg?token=FAL47REO7V)](https://codecov.io/gh/emalvarol/monaco)
![License: LGPL](https://img.shields.io/badge/license-LGPL-blue)


<p align="center">
  <img src="https://raw.githubusercontent.com/emalvarol/mocaco/main/docs/assets/mocaco_logo_v2.svg" alt="mocaco logo" width="200"/>
</p>

Convergence analysis for Monte Carlo series using Polars DataFrames for fastest Python performance.
The library provides a simple API for applying different convergence and stopping criteria to Monte Carlo simulation results.

## Quickstart

```python
import polars as pl
import mocaco as mcc

# Prepare your Monte Carlo samples
df = pl.DataFrame({"it": range(1000), "value": your_samples})

# Create a normalized sample frame
samples = mcc.samples(df, it_col="it", target_col="value")

# Run a convergence criterion
result = mcc.convergence.clt_uni_abs(samples, threshold=0.01)

# Inspect results
print(result.is_converged)  # True/False
print(result.estimate)  # Final cumulative mean
print(result.error)  # Final CLT-based absolute error
print(result.n)  # Number of samples
# and more...
```

## API Overview

| Function | Description |
|----------|-------------|
| `mcc.samples(df, it_col, target_col)` | Create a normalized sample frame from a Polars DataFrame |
| `mcc.convergence(samples, method="...")` | Generic invocation of any registered criterion |
| `mcc.convergence.clt_uni_abs(samples, ...)` | Typed invocation of a specific criterion |
| `mcc.methods()` | List all registered convergence criteria |
| `mcc.describe("clt_uni_abs")` | Get metadata and parameter info for a criterion |

## Available Methods

- [`clt_uni_abs`] — CLT-based absolute error threshold

## Documentation and Changes

Full documentation is available at (https://emalvarol.github.io/mocaco/), in the `docs/` directory, or can be built locally with:

```bash
mkdocs serve
```

Changes and new features are available at (https://github.com/emalvarol/mocaco/blob/main/CHANGELOG.md)

## Installation (Developers)

### Environment

Create the virtual environment and install the project in editable mode with `uv`:

```bash
uv venv
uv sync
uv pip install -e .
```

If it is needed to remove an old environment:

```bash
Remove-Item -Recurse -Force .venv
```

### ruff
```bash
uv run ruff check --fix . && uv run ruff format .
```

### mypy
```bash
uv run mypy src/
```

### pytest
```bash
uv run pytest
```
