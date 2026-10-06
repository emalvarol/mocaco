# Test Coverage Plan

## 1. Overview

This plan defines the strategy for building comprehensive test coverage for the mocaco library. The `tests/` directory is currently empty; this plan establishes the structure, priorities, and scenarios to cover.

**Target:** Cover all breaking-points in parts (api, schemas, wrappers, methods...) to ensure a robust and trustable library.

**Principle:** 
- One assert per test.
- As simple as possible.
- """One line description per test."""

---

## 2. Test Infrastructure

### 2.1 Framework & Tools

| Tool | Purpose |
|------|---------|
| pytest | Test runner (already in dev dependencies) |
| pytest-cov | Coverage reporting |
| pytest-mock | Mocking external dependencies (matplotlib, rich) |
| hypothesis | Property-based testing for numerical criteria |

### 2.2 Directory Structure

```text
tests/
├── conftest.py
├── test_protocols.py
├── test_registry.py
├── test_result.py
├── test_api.py
├── test_wrappers.py
└── methods/
    ├── __init__.py
    └── test_clt_absolute.py
```

### 2.3 Shared Fixtures (conftest.py)

- `sample_df_small` — 10-row Polars DataFrame with known values
- `sample_df_large` — 500-row DataFrame with normally distributed values
- `sample_df_constant` — DataFrame with zero variance
- `sample_df_with_it` — DataFrame with explicit iteration column
- `sample_df_no_it` — DataFrame without iteration column
- `sample_frame` — Pre-built SampleFrame instance
- `clt_params` — Default CLTAbsoluteParams instance

---

## 3. Module Test Plans

### 3.1 `protocols.py` — SampleFrame

**File:** `tests/test_protocols.py`

| Test | Description |
|------|-------------|
| `test_sample_frame_creation_with_it_col` | Valid construction with explicit it_col |
| `test_sample_frame_creation_without_it_col` | Auto-creates `it` column with sequential indices |
| `test_sample_frame_missing_target_col_raises` | ValueError when target_col not in DataFrame |
| `test_sample_frame_empty_df_raises` | ValueError on empty DataFrame |
| `test_sample_frame_non_numeric_target_raises` | TypeError when target is non-numeric |
| `test_sample_frame_non_numeric_it_raises` | TypeError when it_col is non-numeric |
| `test_sample_frame_null_values_raises` | ValueError when target contains nulls |
| `test_sample_frame_nan_values_raises` | ValueError when target contains NaN (float dtype) |
| `test_sample_frame_inf_values_raises` | ValueError when target contains Inf |
| `test_sample_frame_frozen` | Immutability: cannot reassign fields |
| `test_sample_frame_int_target_accepted` | Integer target column is valid |
| `test_sample_frame_filter_cols` | Only it_col and target_col are mantained to save space moving data |

---

### 3.2 `registry.py` — CriterionRegistry

**File:** `tests/test_registry.py`

| Test | Description |
|------|-------------|
| `test_register_decorator` | @registry.register() adds criterion |
| `test_register_programmatic` | registry.register(instance) adds criterion |
| `test_register_duplicate_raises` | ValueError on duplicate name |
| `test_register_overwrite_allows_duplicate` | overwrite=True replaces existing |
| `test_register_empty_name_raises` | ValueError when criterion.name is empty |
| `test_get_existing` | Returns correct criterion instance |
| `test_get_unknown_raises` | ValueError with available names in message |
| `test_names_returns_tuple` | Returns tuple of registered names |
| `test_names_empty_initially` | Empty tuple for fresh registry |
| `test_describe_existing` | describe() prints panel and table (capsys) |
| `test_describe_unknown_prints_error` | describe() prints error for unknown name |
| `test_registry_is_singleton` | Module-level registry is shared |

---

### 3.3 `result.py` — ConvergenceResult & ResultPlotter

**File:** `tests/test_result.py`

| Test | Description |
|------|-------------|
| `test_result_creation` | Valid ConvergenceResult construction |
| `test_result_frozen` | Immutability of dataclass |
| `test_result_diagnostics_default` | diagnostics defaults to empty dict |
| `test_result_to_polars` | Returns the data DataFrame |
| `test_result_to_pandas` | Returns pandas DataFrame |
| `test_result_str` | String representation matches data |
| `test_result_repr` | Compact repr with key fields |
| `test_result_summary_converged` | summary() prints "Converged" (capsys) |
| `test_result_summary_not_converged` | summary() prints "Not Converged" |
| `test_result_summary_with_diagnostics` | Diagnostics appear in summary |
| `test_result_summary_none_estimate` | Handles None estimate gracefully |
| `test_result_plotter_creation` | ResultPlotter instantiated via .plot |
| `test_plotter_evolution_returns_axes` | Returns matplotlib Axes |
| `test_plotter_evolution_missing_cols_raises` | ValueError when required columns missing |
| `test_plotter_evolution_no_convergence` | Plot works when is_converged all False |
| `test_plotter_evolution_with_show_false` | Does not call plt.show() |

---

### 3.4 `api.py` — Convergence Facade

**File:** `tests/test_api.py`

| Test | Description |
|------|-------------|
| `test_convergence_call_with_method` | convergence(samples, method="clt_absolute") |
| `test_convergence_call_unknown_method_raises` | ValueError for unregistered method |
| `test_convergence_getattr_dispatch` | convergence.clt_absolute(samples) |
| `test_convergence_getattr_unknown_raises` | ValueError for unknown attribute |
| `test_convergence_with_eval_frequency` | eval_frequency kwarg triggers wrapper |
| `test_convergence_eval_frequency_unsupported_raises` | TypeError when criterion doesn't support it |
| `test_convergence_params_passed_through` | kwargs become params model fields |
| `test_methods_returns_registered` | mcc.methods() returns expected names |
| `test_describe_existing_method` | mcc.describe("clt_absolute") prints info |
| `test_describe_unknown_method` | mcc.describe("unknown") prints error |
| `test_samples_returns_sample_frame` | mcc.samples() returns SampleFrame |
| `test_samples_passes_columns` | target_col and it_col forwarded correctly |

---

### 3.5 `wrappers.py` — EvalFrequencyWrapper

**File:** `tests/test_wrappers.py`

| Test | Description |
|------|-------------|
| `test_wrapper_delegates_name` | .name matches inner criterion |
| `test_wrapper_delegates_description` | .description matches inner criterion |
| `test_wrapper_delegates_params_type` | .params_type matches inner criterion |
| `test_wrapper_delegates_assumptions` | .assumptions matches inner criterion |
| `test_wrapper_delegates_limitations` | .limitations matches inner criterion |
| `test_wrapper_delegates_references` | .references matches inner criterion |
| `test_wrapper_delegates_result_interpretation` | .result_interpretation matches inner |
| `test_wrapper_delegates_example_usage` | .example_usage matches inner criterion |
| `test_eval_frequency_positive_required` | ValueError on eval_frequency <= 0 |
| `test_eval_frequency_ge_total_rows` | Single evaluation when freq >= rows |
| `test_eval_frequency_lt_total_rows` | Multiple evaluations with concatenated data |
| `test_eval_frequency_appends_final` | Last eval includes remaining rows |
| `test_eval_frequency_diagnostics` | Diagnostics include eval_frequency and n_evaluations |
| `test_eval_frequency_result_fields` | Final result fields from last evaluation |
| `test_wrapper_run_delegates` | Base CriterionWrapper.run() calls inner |

---

### 3.6 `methods/clt_absolute.py` — CLTAbsoluteCriterion

**File:** `tests/methods/test_clt_absolute.py`

| Test | Description |
|------|-------------|
| `test_clt_params_threshold_required` | threshold is required (no default) |
| `test_clt_params_threshold_must_be_positive` | ValidationError on threshold <= 0 |
| `test_clt_params_confidence_range` | ValidationError on confidence outside (0,1) |
| `test_clt_criterion_registered` | Appears in registry after import |
| `test_clt_run_returns_result` | Returns ConvergenceResult instance |
| `test_clt_run_estimate_correct` | Estimate matches expected mean |
| `test_clt_run_n_correct` | n matches DataFrame row count |
| `test_clt_run_error_correct` | Error matches z_score * SEM |
| `test_clt_run_converged_true` | Converges with tight threshold |
| `test_clt_run_converged_false` | Does not converge with strict threshold |
| `test_clt_run_diagnostics` | Diagnostics contain threshold, confidence, z_score |
| `test_clt_run_data_columns` | Output DataFrame has expected columns |
| `test_clt_run_zero_variance` | Handles constant target (std=0) |
| `test_clt_run_single_sample` | Works with n=1 (std=None -> 0) |
| `test_clt_run_large_sample` | Converges with large low-variance sample |
| `test_clt_run_with_eval_frequency` | supports_eval_frequency is True |
| `test_clt_assumptions_non_empty` | Assumptions tuple is populated |
| `test_clt_assumptions_sample_large_enough` | Sample size is more than 30 to allow normal approximation |
| `test_clt_limitations_non_empty` | Limitations tuple is populated |
| `test_clt_references_non_empty` | References tuple is populated |

---

## 4. Edge Cases & Error Handling

Dedicated test class `TestEdgeCases` in each module test file:

- Empty DataFrames
- Single-row DataFrames
- All-identical values (zero variance)
- Very large values (numerical stability)
- Very small values (floating point precision)
- Mixed positive/negative values
- Maximum integer values

---

## 5. Integration Tests

**File:** `tests/test_integration.py`

| Test | Description |
|------|-------------|
| `test_full_pipeline_clt_absolute` | samples -> convergence -> result -> summary |
| `test_full_pipeline_with_eval_frequency` | Full pipeline with eval_frequency wrapper |
| `test_method_discovery_flow` | methods() -> describe() -> convergence() |
| `test_result_export_polars` | to_polars() returns valid DataFrame |
| `test_result_export_pandas` | to_pandas() returns valid DataFrame |
| `test_result_plotting_pipeline` | result.plot.evolution() produces axes |

---

## 6. Coverage Strategy

### 6.1 Running Coverage
Only informative, not mandatory to reach a goal. However, warning the user following the desired coverage by module
```bash
uv run pytest --cov=mocaco --cov-report=term-missing --cov-report=html
```

### 6.2 Desired Coverage by Module

| Module | Target |
|--------|--------|
| protocols.py | 80% |
| registry.py | 60% |
| result.py | 80% |
| api.py | 80% |
| wrappers.py | 80% |
| methods/clt_absolute.py | 80% |
| **Overall** | **>= 70%** |

### 6.3 Known Coverage Gaps (acceptable)

- `plt.show()` interactive display (mock or skip)
- Rich console formatting edge cases (visual only)
- `generate_stubs.py` script (not part of package)

---

## 7. Execution Order

1. `conftest.py` — shared fixtures
2. `test_protocols.py` — foundational data structure
3. `test_registry.py` — method registration
4. `test_result.py` — result representation
5. `test_clt_absolute.py` — core criterion logic
6. `test_wrappers.py` — wrapper behavior
7. `test_api.py` — public API facade
8. `test_integration.py` — end-to-end flows

---

