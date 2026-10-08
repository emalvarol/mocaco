# Changelog

All notable changes to the mocaco project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.2.0 — 2026-08-10

### Added
- Updated documentation and contribution section.
- 

### Changed
- 

### Deprecated
- 

### Fixed
- 

## 0.1.0 — 2026-08-09

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
