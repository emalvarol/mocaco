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

The primary user-facing interface SHOULD remain simple:

```python
import mocaco as mcc
mcc.convergence(samples)
```

A user MUST be able to select a specific convergence method explicitly:

```python
mcc.convergence(samples, method="clt")
```

Method-specific parameters MUST be passed through the same call:

```python
mc.convergence(
    samples,
    method="clt",
    relative_error=0.01,
    confidence=0.95,
)
```

The public API MUST NOT require the user to instantiate internal strategy, registry, parameter, or result classes for ordinary use.

## 3. Convergence Methods

Each convergence criterion MUST be implemented as an independent method.

Methods MUST NOT contain knowledge of the global public API beyond the contract required to execute the criterion.

A method SHOULD encapsulate:

1. its identity;
2. its description;
3. its input parameters;
4. its validation rules;
5. its implementation;
6. its method-specific diagnostics.

Adding a new convergence method SHOULD NOT require modifying the central `convergence()` implementation.

## 4. Method Contract

All convergence methods MUST conform to a common protocol.

The protocol MUST define:

* a method name;
* a parameter specification;
* an execution operation;
* a common result type.

Structural typing through `Protocol` SHOULD be preferred over mandatory inheritance.

Contributors SHOULD be able to implement a new criterion without inheriting from a complex framework hierarchy.

## 5. Parameters

Method-specific parameters MUST be explicitly declared.

Parameter definitions SHOULD be represented by a dedicated parameter object rather than by undocumented `**kwargs`.

Parameter definitions SHOULD provide:

* type information;
* default values;
* validation constraints;
* human-readable descriptions.

The parameter definition SHOULD be the single source of truth for validation and method documentation.

## 6. Results

All convergence methods MUST return a common `ConvergenceResult` abstraction.

The result MUST expose, where applicable:

* whether convergence has been reached;
* the estimated quantity;
* the estimated error;
* the number of samples;
* the method used.

Method-specific information MAY be exposed through a diagnostics structure.

A criterion MUST NOT reduce its complete output to a boolean when additional statistical information is available.

## 7. Registry and Discovery

Convergence methods MUST be discoverable through a registry.

The registry MUST map stable public method names to their implementations.

The central API MUST resolve methods through the registry rather than through hard-coded conditional logic such as:

```python
if method == "clt":
    ...
elif method == "batch_means":
    ...
```

The library SHOULD provide a mechanism to inspect available methods and their configuration.

For example:

```python
mc.methods()
mc.describe("clt")
```

## 8. Extensibility

A contributor SHOULD be able to add a new convergence criterion by adding a self-contained module under:

```text
src/methods/
```

The contributor SHOULD NOT need to modify existing methods.

The contributor SHOULD NOT need to modify the core execution engine unless the new method requires a genuinely new framework capability.

New methods MUST implement the common method contract and MUST return the common result type.

## 9. Separation of Responsibilities

The architecture MUST keep the following responsibilities separate:

* public API;
* method discovery and registration;
* parameter validation;
* convergence computation;
* result representation.

A convergence method SHOULD perform statistical computation, not API routing or registry management.

The registry SHOULD perform discovery, not statistical computation.

The result object SHOULD represent results, not execute convergence logic.

## 10. Scientific Correctness

Statistical terminology MUST be used precisely.

The library MUST distinguish between:

* Monte Carlo error estimation;
* convergence diagnostics;
* stopping criteria;
* confidence intervals;
* uncertainty quantification;
* properties specific to independent Monte Carlo samples.

A method MUST document the assumptions under which its convergence or stopping rule is valid.

The implementation MUST NOT label a diagnostic as a general convergence proof when it only provides an empirical or probabilistic stopping criterion.

## 11. Defaults

Defaults MUST be statistically defensible and explicitly documented.

A default parameter MUST NOT hide a methodological assumption that materially changes interpretation.

Whenever a criterion depends on assumptions such as independence, finite variance, asymptotic normality, or a particular sampling structure, those assumptions MUST be visible in its documentation.

## 12. Stability

Public names, method identifiers, parameter names, and result fields SHOULD be treated as API contracts.

Internal implementation details MAY change without notice provided that public behavior remains compatible.

Method identifiers SHOULD be stable, concise, lowercase, and descriptive.

## 13. Dependencies

The project SHOULD minimize dependencies.

A dependency SHOULD be introduced only when it provides substantial value relative to the complexity it adds.

Scientific functionality MUST NOT depend on a heavyweight framework when equivalent functionality can be implemented clearly with the Python standard library and established scientific packages already required by the project.

## 14. Testing

Every convergence criterion MUST have tests covering:

* valid inputs;
* invalid parameters;
* edge cases;
* expected convergence behavior;
* expected non-convergence behavior;
* result structure.

Tests SHOULD verify statistical properties where practical, rather than only checking implementation-specific numerical values.

## 15. Documentation

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

## 16. Design Principle

Prefer:

```text
simple public API
        +
explicit method contracts
        +
self-contained criteria
        +
common result representation
        +
automatic discovery
```

over:

```text
large inheritance hierarchies
        +
implicit configuration
        +
method-specific public APIs
        +
centralized conditional logic
```

The architecture MUST remain small enough that a new contributor can understand the complete path from:

```python
mc.convergence(samples, method="clt")
```

to the corresponding statistical computation without understanding the entire project.
