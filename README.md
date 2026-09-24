# catable — convergence analysis that works with Polars

Pure-Python library that works with Polars DataFrames. Validate inputs with Pydantic, compute convergence via CLT, expose results as a Polars table `it | criterion | converged`.

- Library name: `catable` (convergence analysis table)
- Works with Polars `DataFrame` via `df.convergence.<criterion>(it_col, target_col, ...)`
- Ty-friendly functional import: `from catable.convergence import clt_absolute`
- Extensible `criterion/` folder — each `.py` file is a criterion (predefined structure, auto-discovered)

## Requirements

- Python >=3.12
- polars >=1.44.2, pydantic >=2.13.5, scipy >=1.18.1
- CPython 3.12.12 (pinned in `.python-version`)

## Dev install — editable + venv (uv)

```bash
# 1. Clone
git clone https://github.com/<you>/catable.git
cd catable

# 2. Create venv + install catable editable + all deps (uses .python-version)
uv sync --group dev          # creates .venv and installs catable editable

# alternative explicit venv
uv venv --python 3.12.12
uv sync --group dev

# 3. Verify
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run python examples/triangular_example.py
```

Install by yourself — exact versions (pin as `>=` in `pyproject.toml`):

```bash
cd C:\Users\outal\GITHUB\catable
uv init                                  # already done
uv add polars pydantic scipy             # -> polars==1.44.2 pydantic==2.13.5 scipy==1.18.1
uv add --dev pytest pytest-cov ruff ty  # -> pytest==9.1.1 pytest-cov==7.1.0 ruff==0.16.8 ty==0.0.84
uv sync --group dev
```

`uv.lock` is committed for reproducibility.

## Usage

```python
import polars as pl
from scipy.stats import triang
import catable  # registers df.convergence.* namespace
from catable.convergence import clt_absolute

# triangular 0-10, mode 5, 50 iterations
vals = triang.rvs(c=0.5, loc=0, scale=10, size=50, random_state=0)
df = pl.DataFrame({"it": list(range(50)), "value": vals.tolist()})

# ty-friendly functional API
table = clt_absolute(df, it_col="it", target_col="value", epsilon=0.1, alpha=0.05, threshold=1.0)
print(table)
# shape: (50, 3) — columns it | criterion | converged

# Polars namespace API
table2 = df.convergence.clt_absolute("it", "value", epsilon=0.1, alpha=0.05, threshold=1.0)
print(table2)
```

Return table:

```
shape: (50, 3)
┌─────┬──────────────┬───────────┐
│ it  ┆ criterion    ┆ converged │
│ --- ┆ ---          ┆ ---       │
│ i64 ┆ str          ┆ bool      │
╞═════╪══════════════╪═══════════╡
│ 0   ┆ clt_absolute ┆ false     │
│ 1   ┆ clt_absolute ┆ false     │
│ ... ┆ ...          ┆ ...       │
└─────┴──────────────┴───────────┘
```

`it_col` and `target_col` are the first two parameters. Pydantic validates that those columns exist in the DataFrame.

## Adding a new criterion

1. Create `src/catable/criterion/<name>.py` following the template in `clt_absolute.py`:
   - Define `class <Name>Params(BaseModel)` and `def compute(df, it_col, target_col, params) -> pl.DataFrame`
2. No registry edit needed — `catable.convergence` and `df.convergence` auto-discover the file.
3. The new method is immediately available as `from catable.convergence import <name>` and `df.convergence.<name>(...)`.

## Quality

```bash
uv run ruff check .
uv run ruff format .
uv run ty check
uv run pytest --cov=catable
```

## License

GPL-3.0-only — see `LICENSE`.
