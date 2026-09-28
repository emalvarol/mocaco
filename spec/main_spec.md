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
├── registry.py
├── result.py
├── protocols.py
│
└── methods/
    ├── __init__.py
    └── clt_absolute.py
```

Responsibilities:

```text
api.py
    Public user-facing API.

registry.py
    Method registration and discovery.

protocols.py
    Structural contracts shared by all methods.

result.py
    Common result representation.

methods/
    Independent convergence criteria. The contributor works mainly here.
```


## 3. Public Entry Point

The API MUST:

1. validate the requested method;
2. retrieve the corresponding method from the registry;
3. allow autocompletion
4. allow parameter inspection
4. execute the method;
5. return a `ConvergenceResult`.

The user MUST be able to define the sample data and select a specific convergence method explicitly to analyze it:

```python
import mocaco as mcc
samples = mcc.samples(df, it_col="it", target_col="value")
result = mcc.convergence(samples, method="clt_absolute")
# OR
result = mcc.convergence.clt_absolute(samples)
```

Method-specific parameters MUST be passed through the same call:

```python
mcc.convergence.clt_absolute(
    samples,
    relative_error=0.01,
)
```

The user can disver method with:

```python
mcc.methods()
mcc.describe("clt_absolute")
```

## 4. Method Protocol

Each criterion SHOULD implement a structural protocol equivalent to:

```python
class Criterion(Protocol):
    name: str
    description: str
    params: type

    def run(
        self,
        samples,
        params,
    ) -> ConvergenceResult:
        ...
```

## 5. Parameter Specification

Every criterion MUST expose a parameter model (input parameters)using pydantic:

Example:

```python
class CLTParams(BaseModel):
    relative_error: float = Field(
        0.01,
        gt=0,
        description="Maximum accepted relative Monte Carlo error.",
    )

    confidence: float = Field(
        0.95,
        gt=0,
        lt=1,
        description="Confidence level.",
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
class CLTCriterion:
    name = "clt"
    description = (
        "Central Limit Theorem based stopping criterion "
        "using relative Monte Carlo error."
    )
    params = CLTParams

    def run(self, samples, params):
        ...
```

## 7. Result Contract

All criteria MUST return a common result object.

The common fields MUST represent information that is meaningful across methods.

Result can have method-specific results

An example of conceptual model is:

```python
@dataclass
class ConvergenceResult:
    converged: bool
    estimate: float
    error: float
    n: int
    method: str
    method_diagnostics: dict
    convergence_evolution: pl.DataFrame
```

## 8. Registry

The registry SHOULD provide a central method lookup mechanism.

The API MUST use the registry rather than hard-coded method dispatch.

The registry SHOULD expose operations equivalent to:

```python
registry.get("clt")
registry.describe("clt")
registry.names()
registry.register(...)
```

New methods are added into the registry and the Convergence class as:
```python
registry.register(
    CLTAbsoluteCriterion()
)
# AND
from .methods import clt_absolute
clt_absolute = staticmethod(clt_absolute)
```
