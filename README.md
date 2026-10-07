# mocaco
# mocaco

[![CI](https://github.com/emalvarol/mocaco/actions/workflows/ci.yml/badge.svg)](https://github.com/emalvarol/mocaco/actions/workflows/ci.yml)
![Python Versions](https://img.shields.io/badge/python-3.12%20|%203.13%20|%203.14-blue)
![License: LGPL](https://img.shields.io/badge/license-LGPL-blue)

Convergence analysis for Monte Carlo series using Polars DataFrames.

<p align="center">
  <img src="assets/Logo_v1.png" alt="mocaco logo" width="400"/>
</p>

The library provides a simple API for applying different convergence and
stopping criteria to Monte Carlo simulation results.

## Quickstart

```python
import polars as pl
import mocaco as mcc

# Prepare your Monte Carlo samples
df = pl.DataFrame({"it": range(1000), "value": your_samples})

# Create a normalized sample frame
samples = mcc.samples(df, it_col="it", target_col="value")

# Run a convergence criterion
result = mcc.convergence.clt_absolute(samples, threshold=0.01)

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
| `mcc.convergence.clt_absolute(samples, ...)` | Typed invocation of a specific criterion |
| `mcc.methods()` | List all registered convergence criteria |
| `mcc.describe("clt_absolute")` | Get metadata and parameter info for a criterion |

## Available Methods

- [`clt_absolute`](docs/methods/clt_absolute.md) — CLT-based absolute error threshold

## Documentation

Full documentation is available in the `docs/` directory or can be built with:

```bash
mkdocs serve
```

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
