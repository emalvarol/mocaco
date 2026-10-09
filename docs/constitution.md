# Constitution of mocaco

## 1. Purpose

This project provides a small, extensible Python library for diagnosing convergence and stopping conditions in Monte Carlo simulations.

The library MUST prioritize:

* a simple and intuitive public API;
* statistically well-defined convergence criteria;
* explicit and inspectable method configuration;
* consistent result objects;
* easy extension by independent contributors;
* minimal coupling between the public API and individual convergence methods.

The library MUST NOT optimize for API complexity merely to accommodate hypothetical future use cases.

## 2. Public API

The primary user-facing interface SHOULD remain simple.

The public API MUST NOT require the user to instantiate internal strategy, registry, parameter, or result classes for ordinary use.

The public API consists of:

* `mcc.samples(df, *, target_col, it_col=None)` — construct a validated `SampleFrame`;
* `mcc.convergence(samples, *, method, **kwargs)` — execute a criterion by name;
* `mcc.convergence.<criterion>(samples, **kwargs)` — execute a criterion as a typed attribute;
* `mcc.methods()` — list all registered criteria;
* `mcc.describe(name)` — inspect a criterion's metadata and parameters.

The `Convergence` class acts as a callable namespace: `__call__` resolves by name through the registry; `__getattr__` resolves registered criteria as callable attributes. Both paths time the execution and populate `execution_time_sec` on the result.

## 3. Methods
### 3.1 Convergence Methods by non-expert contibutors

Each convergence criterion MUST be implemented as an independent method containing primarly its input parameters its math logic and its API use.

Contributors MUST be able to easily add a new criterion even being non python experts following a method protocol. The addition is done within a single criterion module in `methods/` by decorating the criterion class with `@registry.register()`.

Method identifiers SHOULD be stable, concise, lowercase, and descriptive.

Every public convergence method MUST document:

* purpose;
* statistical assumptions;
* parameters;
* defaults;
* interpretation of the result;
* limitations;
* example usage.

The documentation MUST correspond to the actual implementation.

Parameter documentation MUST NOT be maintained independently when it can be generated from the parameter specification.

### 3.2 Protocol

The protocol of the method MUST define:

* a method name;
* a parameter specification;
* an execution operation;
* a common result type;
* statistical assumptions and limitations;
* result interpretation guidance;
* an example usage;
* scientific references.

The full protocol is:

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

    def run(self, samples: SampleFrame, params: Any) -> ConvergenceResult: ...
```

### 3.3 Parameters

Method-specific parameters MUST be explicitly declared.

Parameter definitions SHOULD be represented by a dedicated parameter object rather than by undocumented `**kwargs`.

Parameter definitions SHOULD provide:

* type information;
* default values;
* validation constraints;
* human-readable descriptions.

The parameter definition SHOULD be the single source of truth for validation and method documentation.

### 3.4 Results

All convergence methods MUST return a common `ConvergenceResult` abstraction.

< Still needs design >

### 3.5 Registry and Discovery

Convergence methods MUST be discoverable through a registry.

The registry MUST map stable public method names to their implementations.

The registry MUST support registration both programmatically, `registry.register(criterion)`, and as a class decorator, `@registry.register()`.

The central API MUST resolve methods through the registry rather than through hard-coded conditional logic.

The library SHOULD provide a mechanism to inspect available methods and their configuration.

### 3.6 SampleFrame Validation

The `SampleFrame` dataclass is the single input contract for all criteria. It MUST validate at construction time:

* both `target_col` and `it_col` must exist in the source DataFrame;
* both columns must be numeric (integer or float);
* the target column must not contain Null, NaN, or Inf values;
* if `it_col` is omitted, a sequential `it` column (1-indexed) MUST be auto-created.

### 3.7 Result Contract

`ConvergenceResult` is a frozen dataclass providing:

| Field | Type | Description |
|-------|------|-------------|
| `method` | `str` | Criterion name. |
| `n` | `int` | Number of samples used in the final estimate. |
| `n_col` | `str` | Name of the n column in the diagnostic data. |
| `estimate` | `float \| None` | Final estimate of the target quantity. |
| `estimate_col` | `str` | Name of the estimate column in the diagnostic data. |
| `error` | `float \| None` | Final estimated error. |
| `error_col` | `str` | Name of the error column in the diagnostic data. |
| `is_converged` | `bool \| None` | Whether the final state satisfies the criterion. |
| `is_converged_col` | `str` | Name of the is_converged column in the diagnostic data. |
| `data` | `pl.DataFrame` | Full diagnostic DataFrame generated by the method/wrapper. |
| `execution_time_sec` | `float \| None` | Execution time measured by the `Convergence` wrapper. |
| `diagnostics` | `dict[str, Any]` | Method-specific diagnostic information. |

`ConvergenceResult` MUST also provide:

* `summary()` — rich console output of the convergence status;
* `to_polars()` / `to_pandas()` — conversion to DataFrame objects;
* `plot` property returning a `ResultPlotter` instance.

`ResultPlotter` MUST provide an `evolution()` method that visualizes the estimate, error band, and convergence point (requires `matplotlib`).

### 3.8. Scientific Correctness

Statistical terminology MUST be used precisely.

The library MUST distinguish between:

* Monte Carlo error estimation;
* convergence diagnostics;
* stopping criteria;
* confidence intervals;
* uncertainty quantification;
* properties specific to independent Monte Carlo samples.

A method MUST document the assumptions under which its convergence or stopping rule is valid.

Scientific paper citations are required.

The implementation MUST NOT label a diagnostic as a general convergence proof when it only provides an empirical or probabilistic stopping criterion.

Defaults MUST be statistically defensible and explicitly documented.

Whenever a criterion depends on assumptions such as independence, finite variance, asymptotic normality, or a particular sampling structure, those assumptions MUST be visible in its documentation.

## 4. Separation of Responsibilities

The architecture MUST keep the following responsibilities separate:

* public API;
* method discovery and registration;
* parameter validation;
* convergence computation;
* result representation.


## 5. Dependencies

The project SHOULD minimize dependencies.

A dependency SHOULD be introduced only when it provides substantial value relative to the complexity it adds.


## 6. Testing

Every convergence criterion MUST have tests covering:

* valid inputs;
* invalid parameters;
* edge cases;
* expected convergence behavior;
* expected non-convergence behavior;
* result structure.

Tests SHOULD verify statistical properties where practical, rather than only checking implementation-specific numerical values.

## 7. Automation Scripts

The `scripts/` directory contains automation tooling:

| Script | Purpose |
|--------|---------|
| `generate_stubs.py` | Regenerate `api.pyi` from the registry for IDE autocompletion. |
| `generate_docs.py` | Generate documentation from criterion metadata. |
| `generate_config.yaml` | Configuration for stub and doc generation.

The `api.pyi` file is auto-generated and MUST NOT be edited manually. It is regenerated by running `python scripts/generate_stubs.py`.
