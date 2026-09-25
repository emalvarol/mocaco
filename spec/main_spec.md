# General Design Specification

## 1. Scope

This specification defines the architecture for convergence and stopping criteria in the mocaco library.

The initial implementation is intended for standard Monte Carlo data, with the architecture designed to support additional criteria such as:

* Central Limit Theorem based error criteria;
* relative-error criteria;
* absolute-error criteria;
* batch-based variance estimation;
* sequential stopping rules;
* alternative uncertainty estimators;
* future criteria for correlated simulation output.

The design MUST allow these criteria to coexist behind one public API.

---

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
    Independent convergence criteria.
```

A method module SHOULD contain all method-specific code and SHOULD NOT depend on unrelated method implementations.

---

## 3. Public Entry Point

The primary entry point MUST be:

```python
mcc.convergence(samples, method="clt", **parameters)
```

The API MUST:

1. validate the requested method;
2. retrieve the corresponding method from the registry;
3. construct and validate its parameter object;
4. execute the method;
5. return a `ConvergenceResult`.

Conceptually:

```python
def convergence(samples, method="clt", **kwargs):
    criterion = registry.get(method)
    params = criterion.params(**kwargs)
    return criterion.run(samples, params)
```

The exact implementation MAY differ, but these responsibilities SHOULD remain explicit.

---

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

The protocol MUST be sufficient for the API and discovery mechanisms to operate without knowing the implementation details of the criterion.

A method MAY expose additional capabilities internally, but these MUST NOT be required by the core API.

---

## 5. Parameter Specification

Every criterion MUST expose a parameter model.

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

The preferred implementation may use Pydantic or an equivalent strongly structured mechanism.

The parameter model MUST NOT contain the statistical execution logic.

---

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

Its implementation is responsible for computing quantities such as:

```text
estimate
sample variance
MCSE
critical value
confidence interval
relative error
convergence status
```

The exact statistical formulation MUST be documented separately from the architectural implementation.

---

## 7. Result Contract

All criteria MUST return a common result object.

A minimal conceptual model is:

```python
@dataclass
class ConvergenceResult:
    converged: bool
    estimate: float
    error: float
    n: int
    method: str
    diagnostics: dict
```

The common fields MUST represent information that is meaningful across methods.

Method-specific information SHOULD be stored in:

```python
diagnostics
```

For example:

```python
result.diagnostics
```

may contain:

```python
{
    "mcse": 0.0021,
    "confidence": 0.95,
    "relative_error": 0.0017,
    "critical_value": 1.96,
}
```

The result object SHOULD also permit future extension without requiring every method to expose identical internal diagnostics.

---

## 8. Registry

The registry SHOULD provide a central method lookup mechanism.

Conceptually:

```python
REGISTRY = {
    "clt": CLTCriterion(),
    "batch_means": BatchMeansCriterion(),
}
```

The API MUST use the registry rather than hard-coded method dispatch.

The registry SHOULD expose operations equivalent to:

```python
registry.get("clt")
registry.list()
registry.register(...)
```

---

## 9. Method Discovery

The library SHOULD expose introspection facilities such as:

```python
mcc.methods()
```

which returns available public method identifiers.

The library SHOULD also expose:

```python
mcc.describe("clt")
```

which returns a structured representation containing at least:

```text
name
description
parameters
defaults
parameter descriptions
result type
statistical assumptions
```

A structured representation SHOULD be preferred internally so that text, CLI output, notebook interfaces, and generated documentation can all consume the same metadata.

---

## 10. Extension Workflow

A contributor adding a new criterion SHOULD follow this workflow:

### Step 1

Create:

```text
src/methods/my_method.py
```

### Step 2

Define a parameter model:

```python
class MyMethodParams(...):
    ...
```

### Step 3

Define the criterion:

```python
class MyMethodCriterion:
    name = "my_method"
    description = "..."
    params = MyMethodParams

    def run(self, samples, params):
        ...
```

### Step 4

Register the criterion.

The contributor SHOULD NOT need to modify:

```text
api.py
result.py
```

unless the new method introduces a new framework requirement.

---

## 11. Registration Mechanism

For the initial version, explicit registration is preferred because it is easy to understand and debug.

For example:

```python
register("clt", CLTCriterion())
```

The architecture SHOULD NOT introduce plugin complexity before it is justified by real use cases.

---

## 12. Error Handling

The API SHOULD distinguish at least three classes of errors:

### Invalid method

```python
mcc.convergence(x, method="unknown")
```

MUST produce an explicit error identifying the requested method and available alternatives.

### Invalid parameters

```python
mcc.convergence(x, method="clt", relative_error=-1)
```

MUST fail during parameter validation, before statistical computation begins.

### Invalid data

Examples include:

* empty samples;
* insufficient sample count;
* non-numeric values;
* incompatible dimensions;
* NaN or infinite values where unsupported.

Data validation SHOULD occur before method execution.

---

## 13. Data Handling

Methods SHOULD operate on a well-defined internal representation of samples.

The core library SHOULD establish:

* accepted array-like inputs;
* dimensionality conventions;
* handling of missing values;
* behavior for scalar versus vector-valued quantities.

Methods SHOULD NOT each independently invent their own interpretation of sample arrays.

A common normalization layer MAY be introduced if several methods require identical preprocessing.

---

## 14. Scientific Assumptions

Each method MUST explicitly declare its statistical assumptions.

For example, a CLT-based criterion may require assumptions concerning:

```text
independence or weak dependence;
finite variance;
asymptotic normality;
sample size;
non-zero reference estimate for relative error.
```

These assumptions MUST be part of the method documentation.

The framework MUST distinguish:

```text
"the stopping criterion reports convergence"
```

from:

```text
"the estimator has mathematically converged."
```

A stopping criterion is an operational decision rule and MUST NOT be represented as a universal mathematical proof of convergence.

---

## 15. API Evolution

Not defiend yet

## 16. Object Relationships

The intended architecture is:

```text
                    ┌─────────────────┐
                    │ Public API      │
                    │ convergence()   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Registry     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        CLTCriterion   BatchCriterion   OtherCriterion
              │              │              │
              ▼              ▼              ▼
          CLTParams      BatchParams     OtherParams
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Convergence     │
                    │ Result          │
                    └─────────────────┘
```

For now only CLTAbsoluteCriterion is added

The dependency direction SHOULD remain:

```text
API → Registry → Criterion → Result
                    ↓
                 Params
```

Individual criteria MUST NOT depend on the public API.

---

## 17. Design Priorities

When architectural trade-offs arise, the project SHOULD prioritize, in order:

1. scientific correctness;
2. clarity of the public API;
3. explicit statistical assumptions;
4. extensibility;
5. testability;
6. implementation simplicity;
7. performance optimizations that are supported by actual profiling.

The project SHOULD avoid abstraction for abstraction's sake.

A design is preferred when the architecture of the library can be understood from a small number of concepts:

```text
Method
Parameter Model
Registry
Result
```

These four concepts should constitute the core mental model for contributors.
