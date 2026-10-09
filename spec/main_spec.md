# General Design Specification

## 1. Scope

This specification defines the architecture for convergence and stopping criteria in the mocaco library.

The initial implementation is intended for standard Monte Carlo data, with the architecture designed to support additional criteria such as:

* Central Limit Theorem based error criteria;
* relative-error criteria;
* absolute-error criteria;

The design MUST allow these criteria to coexist behind one public API.


## 2. Package Structure

The initial package SHOULD follow this structure:

```text
src/
├── api.py
├── api.pyi
├── registry.py
├── result.py
├── protocols.py
│
├── methods/
│   ├── __init__.py
│   └── clt_uni_abs.py
│
scripts/
├── generate_stubs.py
├── generate_docs.py
└── generate_config.yaml
```

Responsibilities:

```text
api.py
    Public user-facing API.

api.pyi
    Auto-generated type stubs for IDE autocompletion and type checking.

registry.py
    Method registration and discovery.

protocols.py
    Structural contracts shared by all methods (SampleFrame, Criterion).

result.py
    Common result representation (ConvergenceResult, ResultPlotter).

methods/
    Independent convergence criteria. The contributor works mainly here.

scripts/
    Automation scripts for stub and doc generation.
```


## 3. Public Entry Point

The API MUST:

1. validate the requested method;
2. retrieve the corresponding method from the registry;
3. allow autocompletion (via `api.pyi`);
4. allow parameter inspection;
5. execute the method;
6. return a `ConvergenceResult`.

The user MUST be able to define the sample data and select a specific convergence method explicitly to analyze it:

```python
import mocaco as mcc

samples = mcc.samples(df, target_col="value", it_col="it")
result = mcc.convergence(samples, method="clt_uni_abs")
# OR
result = mcc.convergence.clt_uni_abs(samples)
```

Method-specific parameters MUST be passed through the same call:

```python
mcc.convergence.clt_uni_abs(
    samples,
    threshold=0.1,
)
```

The user can discover methods with:

```python
mcc.methods()
mcc.describe("clt_uni_abs")
```

### 3.1 SampleFrame

The `samples()` function creates a `SampleFrame` — a frozen, validated, and read-only representation of the input data:

```python
samples = mcc.samples(df, target_col="value", it_col="it")
```

`SampleFrame` validates at construction time:

* both `target_col` and `it_col` must exist in the DataFrame;
* both columns must be numeric;
* the target column must not contain Null, NaN, or Inf values;
* if `it_col` is omitted, a sequential `it` column is auto-created (1-indexed).

### 3.2 Convergence Class

The public `convergence` object is an instance of the `Convergence` class, which acts as a callable namespace:

```python
class Convergence:
    def __call__(self, samples, *, method, **kwargs) -> ConvergenceResult: ...
    def __getattr__(self, name) -> Callable[..., ConvergenceResult]: ...
```

* `__call__` resolves a criterion by name from the registry and executes it.
* `__getattr__` resolves registered criteria as callable attributes, enabling IDE autocompletion via `api.pyi`.
* Both paths execute through `_execute_criterion`, which constructs params, runs the criterion, and records `execution_time_sec`.


## 4. Method Protocol

Each criterion MUST implement a structural protocol equivalent to:

```python
class Criterion(Protocol):
    name: str
    description: str
    params_type: type[Any]

    assumptions: ClassVar[Sequence[str]]
    limitations: ClassVar[Sequence[str]]
    result_interpretation: str
    example_usage: str
    references: ClassVar[Sequence[str]]

    def run(
        self,
        samples: SampleFrame,
        params: Any,
    ) -> ConvergenceResult: ...
```

### 4.1 Protocol Fields

Every criterion MUST expose:

| Field | Purpose |
|-------|---------|
| `name` | Stable public identifier (e.g. `"clt_uni_abs"`). |
| `description` | One-line summary of the criterion. |
| `params_type` | Pydantic model defining input parameters. |
| `assumptions` | Statistical assumptions required for validity. |
| `limitations` | Known limitations of the criterion. |
| `result_interpretation` | How to interpret the returned result. |
| `example_usage` | Minimal code example. |
| `references` | Academic or documentation references. |


## 5. Parameter Specification

Every criterion MUST expose a parameter model (input parameters) using pydantic:

Example:

```python
class InputParams(BaseModel):
    threshold: float = Field(
        ...,
        gt=0,
        description="Maximum accepted absolute Monte Carlo error.",
    )

    confidence_level: float = Field(
        0.95,
        gt=0,
        lt=1,
        description="Confidence level used for the CLT margin of error.",
    )

    eval_frequency: int | None = Field(
        default=None,
        gt=0,
        description="Step interval for periodic evaluation of convergence history natively in Polars.",
    )
```

The parameter model serves as the source of truth for:

* validation;
* defaults;
* type information;
* introspection;
* generated documentation.


## 6. Example Criterion

A CLT-based criterion SHOULD conceptually have the following structure:

```python
class CLTAbsoluteCriterion:
    name = "clt_uni_abs"
    description = "Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold."
    params_type = InputParams

    assumptions = ("Samples are independent and identically distributed (i.i.d.).", ...)
    limitations = ("This is a probabilistic stopping criterion, not a proof of convergence.", ...)
    result_interpretation = (
        "is_converged is True when the CLT-based absolute error has stayed below the threshold..."
    )
    example_usage = """..."""
    references = ("https://en.wikipedia.org/wiki/Central_limit_theorem",)

    def run(self, samples: SampleFrame, params: InputParams) -> ConvergenceResult: ...
```


## 7. Result Contract

All criteria MUST return a common result object.

The common fields MUST represent information that is meaningful across methods.

Result can have method-specific results via the `diagnostics` dict.

The actual model is:

```python
@dataclass(frozen=True)
class ConvergenceResult:
    # Common outputs to all criterions
    method: str
    n: int
    n_col: str
    estimate: float | None
    estimate_col: str
    error: float | None
    error_col: str
    is_converged: bool | None
    is_converged_col: str

    # Built by Wrapper or by the criterion default
    data: pl.DataFrame

    # Performance
    execution_time_sec: float | None = None

    # Method-specific outputs
    diagnostics: dict[str, Any] = field(default_factory=dict)
```

### 7.1 Result Methods

`ConvergenceResult` provides the following helpers:

| Method | Description |
|--------|-------------|
| `summary()` | Print a rich formatted summary to the console. |
| `to_polars()` | Return the diagnostic DataFrame as Polars. |
| `to_pandas()` | Return the diagnostic DataFrame as Pandas. |
| `plot` | Property returning a `ResultPlotter` instance. |

### 7.2 ResultPlotter

`ResultPlotter` provides plotting capabilities:

```python
result.plot.evolution(show=True)
```

Plots the estimate line, error band, and convergence point. Requires `matplotlib` (installed via `uv pip install mocaco[plot]`).


## 8. Registry

The registry SHOULD provide a central method lookup mechanism.

The API MUST use the registry rather than hard-coded method dispatch.

The registry MUST support both registration modes:

```python
# Decorator usage (class-level)
@registry.register()
class CLTAbsoluteCriterion: ...


# Programmatic usage (instance-level)
registry.register(CLTAbsoluteCriterion())
```

The registry SHOULD expose operations equivalent to:

```python
registry.get("clt_uni_abs")
registry.describe("clt_uni_abs")
registry.names()
registry.register(...)
```

`describe()` renders rich console output (Panel + Table) showing the method description and parameter details.

New methods are added by creating a single module in `methods/` whose criterion class is decorated with `@registry.register()`:

```python
from mocaco.registry import registry


@registry.register()
class CLTAbsoluteCriterion: ...
```

The methods package auto-discovers and imports every module in `methods/`, so the decorator runs at import time and no manual registration is needed. The `Convergence` façade resolves registered criteria automatically through the registry, so no manual changes to `api.py` are needed. The type stub file `api.pyi` is regenerated from the registry by running `python scripts/generate_stubs.py`.
