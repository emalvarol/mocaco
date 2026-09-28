# mocaco

Convergence analysis for Monte Carlo series using Polars DataFrames.

The library provides a simple API for applying different convergence and
stopping criteria to Monte Carlo simulation results.

## Installation

Create the virtual environment and install the project in editable mode with `uv`:

```bash
uv venv
uv sync
uv pip install -e .
```

If it is needed to remove an old environment

```bash
Remove-Item -Recurse -Force .venv
```