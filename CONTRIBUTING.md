# Contributing to mocaco

## Philosophy

mocaco is an extensible library for convergence analysis of Monte Carlo simulations. It is designed to be easy to use by both users and developers (non-python expert friendly). Adding a new convergence criterion requires **only one Python file** — no changes to the public API, registry, or documentation are needed manually. The project uses an auto-discovery mechanism that process all modules from `src/mocaco/methods/`, so a new criterion is immediately integrated in the library after its module is created.

Friendly remainder: The maintainer (me) is not (yet) a python expert and likely the library can be improved in many ways. If you are a real expert and you desire to pull changes across the libary itself I will be very happy.

## Keep in mind

Each convergence criterion lives as a single module in `src/mocaco/methods/`. The main aspect to remember is that the method will recive a formated polar DataFrame and will return an structured results, including another polar DataFrame. The imput and output data is also explained on this guide as well as the method file structure (see clt_absolute.py method to see an example).

### Input data

The file `src/mocaco/protocols.py` defines the class `SampleFrame` which make sure the input data is standarized. It defines which columns must be used by the method, which will be available for the method. Actually the defined columns names are:

- `df` (pl.DataFrame) Source Polars DataFrame.
- `it_col` (str) Column containing the iteration/order of the samples.
- `target_col` (str) Column containing the quantity to analyze.

The file `src/mocaco/protocols.py` also defines the structure of the method, and particularly the run method, which includes:

- `samples` (`SampleFrame`) The structured input
- `params` The method parameters.

This structure is which allow automatic method discovery and documentation among others. Here data columns are used as `samples.target_col` or `samples.it_col`, while method parameters are used as `params.confidence_level`, for example.

### Output data

The file `src/mocaco/result.py` defines the class `ConvergenceResult`, which contains all the results a method must or can return. See it or see the module clt_absolute.py as a reference. This ensures all methos can be used by the library and be easyly plotted.

## Method structure

Said this, the detailed structure for a new method is as follows:

### 1. Imports and setup

One-line module string description and mandatory basic modules and imports from `mocaco`. Typically includes `polars`, `pydantic`, `scipy.stats`, the `registry`, and `ConvergenceResult`.

### 2. Parameter specification (`params_type`)

A **pydantic `BaseModel`** defines the criterion's input parameters. This is the single source of truth for validation and documentation. Each field must provide:

- Type information
- Default values if apply
- Validation constraints (e.g., `gt`, `lt`)
- Human-readable descriptions

Using pydantic ensures automatic validation, consistent API docs, and generated parameter documentation.

### 3. Criterion class (decorated with `@registry.register()`)

The main class must:

- Assign a stable, concise, lowercase, descriptive `name` (e.g., `"clt_absolute"`)
- Set `params_type` to the parameter model
- Optionally set `supports_eval_frequency`
- Provide documentation sections: `description`, `assumptions`, `limitations`, `result_interpretation`, `example_usage`, `references`
- Implement a `run(samples, params)` method that returns a `ConvergenceResult`

The `@registry.register()` decorator handles automatic registration — no manual API updates are needed.

### 4. Execution logic (`run` method)

The core convergence computation. Takes a `SampleFrame` and validated `params`, returns a `ConvergenceResult` with the common fields: `method`, `n`, `estimate`, `error`, `is_converged`, `diagnostics`, `data`, among others.

---

## Formatting and code quality

Once a method is created whit the desired structure:

- Run `uv run ruff check --fix . && uv run ruff format .` to ensure Ruff formatting and linting standards.
- Run `uv run mypy src/` for type checking — all convergence methods must be compatible with the project's strict mypy configuration.
- GitHub Actions CI runs on every pull request across Python 3.12, 3.13, and 3.14, including ruff, mypy, and pytest.

## Documentation

Documentation is **automatically generated** from the method's parameter specification and class attributes. This is why the following parameters are **mandatory** on every method:

- `params_type` — pydantic BaseModel; its fields are the single source of truth for validation and docs
- `name` — stable identifier, used in API endpoints and documentation
- `assumptions` — explicitly documented statistical assumptions (i.i.d., finite variance, CLT applicability, etc.)
- `limitations` — what the criterion does not guarantee
- `result_interpretation` — explanation of each `ConvergenceResult` field
- `example_usage` — minimal working example
- `references` — academic citations where applicable

The `docs/index.md` and method docs in `docs/methods/` are regenerated by running `uv run python scripts/generate_docs.py`. 

## Testing

Tests are **optional but highly recommended**. A new criterion should include tests covering:

- Valid inputs
- Invalid parameters
- Edge cases
- Expected convergence behavior
- Expected non-convergence behavior
- Result structure

If tests are not provided, the maintainer will likely contact the contributor to clarify doubts and add the required test coverage before merging.

---