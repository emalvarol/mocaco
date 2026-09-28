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

## 3. Methods
### 3.1 Convergence Methods by non-expert contibutors

Each convergence criterion MUST be implemented as an independent method containing primarly its input parameters its math logic and its API use.

Contributors MUST be able to easily add a new criterion even being non python experts following a method protocol. The addition is done within the criterion module plus a single registration line in `methods/__init__.py`. The public API MUST integrate the new criterion automatically through the registry-backed façade, without manual changes to `api.py`. The type stub file `api.pyi` MUST be regenerated from the registry by running `scripts/generate_stubs.py`.

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
* a common result type.


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

The central API MUST resolve methods through the registry rather than through hard-coded conditional logic.

The library SHOULD provide a mechanism to inspect available methods and their configuration.


### 3.6. Scientific Correctness

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


