# Changelog

All notable changes to the mocaco project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Improve documentation and examples
    - economic results
    - basic examples to show all the mocaco capabilities

## [0.3.1] — 2026-10-21

### Added
- Example with real data `10_water_depht`.
- More tests for plots.

### Added
- Improved `residual_error_evolution` method within `ResultPlotter` class.

### Fixed
- Proper vertical convergence line plot when convergence true and false alternates.

## [0.3.0] — 2026-10-15

### Added
- Improved logo
- Code coverage badget
- Toml classifiers
- GitHub release in Actions
- New clt_uni_rel method: Central Limit Theorem based convergence criterion using a relative Monte Carlo error threshold.
- Tests to cover new methods, GroupedConvergenceResult and group_cols
- str, list and dic selector for GroupedConvergenceResult instead of the tuple key verbosity
- `residual_error` field on `ConvergenceResult` (`max(0, |error| - threshold)`), populated by `clt_uni_abs` and `clt_uni_rel`
- `GroupedConvergenceResult.residual_error_by(keep=...)` to aggregate residual errors over grouping dimensions
- `GroupedConvergenceResult.data_residual_error_by(keep=..., filter=...)` returning the evolution of the aggregated residual error with `agg_<column>`, `res_error` and `is_converged` columns
- `ResultPlotter.residual_error_evolution(keep=..., filter=..., show=...)` to plot the aggregated residual evolution for grouped results
- New parameter to criterion protocol to specify if criterions works with `univariate` or `multivariate` dataframes

### Changed
- `target_col` accept now both `str` and `list[str]`

## [0.2.0] — 2026-10-14

### Added
- Updated documentation and contribution section.
- Method execution time measurement and benchmark to compare better method implementation.
- Compiled automatic documentation, stubs and publish with GITHUB Actions into ci/cd implementation.
- Updated optional and default dependencies.
- Added GroupedConvergenceResult result and group_cols as input columns to support automatic convergence estimates on groups.
- Tests to conver new features
- Added residual error agregation capability when group_cols is provided

### Changed
- clt_absolute method is now clt_uni_abs
- criterion protocol now can return a single ConvergenceResult or a GroupedConvergenceResult to support group_cols on methods

### Removed
- wrapper and support_eval_frequency removed (low performance compared to support at method module level).


## [0.1.0] — 2026-10-07

### Added
- Initial library structure: `src/mocaco/`, `docs/`, `tests/`, `scripts/`
- Core convergence criterion: `clt_absolute` — Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold
- Registry auto-discovery pattern — `pkgutil` auto-imports all modules in `src/mocaco/methods/`
- `ConvergenceResult` abstraction with common fields: `method`, `n`, `estimate`, `error`, `is_converged`, `diagnostics`, `data`
- Public API: `mcc.samples(df, it_col, target_col)`, `mcc.convergence(samples, method="...")`, `mcc.convergence.clt_absolute(samples, ...)`, `mcc.methods()`, `mcc.describe("name")`
- Documentation: `constitution.md`, `roadmap.md`, `main_spec.md`, `docs/index.md`, `docs/methods/clt_absolute.md`
- Test suite foundation: `tests/` with tests for API, registry, protocols, wrappers, results, integration, and methods
- Project configuration: `pyproject.toml`, `AGENTS.md`, `LICENSE`, `README.md`, `uv.lock`, `.gitignore`
- Build system: hatchling-based wheel build
- `# 8. CONTRIBUTING.md Guidelines for external developers registering new convergence criteria.` — New contributing guidelines document at repository root, covering the philosophy of adding only one Python file to register a new convergence criterion, the required file structure (imports, pydantic `params_type`, `@registry.register()` decorator, `run` method), formatting and code quality (ruff, mypy, GitHub Actions), auto-generated documentation, and optional but recommended testing.
- `# 9. CHANGELOG.md Project Files` — Changelog file created for release notes, following Keep a Changelog format.
