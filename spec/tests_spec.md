# Test Coverage Plan

## 1. Overview

This document specifies the test strategy for the mocaco library and the
inventory of tests that implement it.

**Current state:** the `tests/` suite is implemented and green — **154 tests**
across seven modules (`tests/` + `tests/methods/`). This document is kept in
sync with the suite and serves as the reference for what is covered and where
new tests belong.

**Target:** Cover all breaking-points in parts (api, protocols, registry,
result, methods...) to ensure a robust and trustable library.

**Principle:**

- One assert per test.
- As simple as possible.
- """One line description per test."""

---

## 2. Test Infrastructure

### 2.1 Framework & Tools

| Tool | Purpose |
|------|---------|
| pytest | Test runner (dev dependency) |
| pytest-cov | Coverage reporting |
| pytest-benchmark | Performance benchmarks under `benchmarks/` |
| hypothesis | (Optional) property-based testing for numerical criteria |

Note: `pytest-mock` is not required because plotting is exercised against the
real `matplotlib` backend switched to `Agg`.

### 2.2 Directory Structure

```text
tests/
├ conftest.py
├ test_protocols.py
├ test_registry.py
├ test_result.py
├ test_api.py
├ test_integration.py
└ methods/
    ├── __init__.py
    ├── test_clt_uni_abs.py
    └── test_clt_uni_rel.py

benchmarks/
├ test_eval_frequency_comp.py
├ compare.py
└ results.json
```

### 2.3 Shared Fixtures (conftest.py)

Data fixtures:

| Fixture | Description |
|---------|-------------|
| `sample_df_small` | 10-row Polars DataFrame with known values (1..10) |
| `sample_df_large` | 500-row DataFrame with normally distributed values (seeded) |
| `sample_df_constant` | 30-row DataFrame with zero variance (all `5.0`) |
| `sample_df_with_it` | 30-row DataFrame with explicit `it` column |
| `sample_df_no_it` | 10-row DataFrame without an iteration column |
| `sample_df_grouped` | 80-row DataFrame with two groups (`group` = a/b), 40 rows each (seeded) |
| `sample_df_grouped_multi` | 160-row DataFrame with a 2x2 grid (`cat1` x `cat2`), 40 rows each (seeded) |

SampleFrame fixtures:

| Fixture | Description |
|---------|-------------|
| `sample_frame` | `SampleFrame` over `sample_df_with_it` (`target_col="measurement"`) |
| `sample_df_no_it_frame` | `SampleFrame` over `sample_df_no_it` (auto-created `it`) |
| `sample_frame_constant` | `SampleFrame` over `sample_df_constant` |
| `sample_frame_grouped` | `SampleFrame` with `group_cols="group"` |
| `sample_frame_grouped_multi` | `SampleFrame` with `group_cols=["cat1", "cat2"]` |

Parameter fixtures:

| Fixture | Description |
|---------|-------------|
| `clt_params` | `clt_uni_abs.InputParams(threshold=0.1, confidence_level=0.95)` |
| `clt_rel_params` | `clt_uni_rel.InputParams(threshold=0.05, confidence_level=0.95)` |

Result fixtures:

| Fixture | Description |
|---------|-------------|
| `make_convergence_result` | Factory returning a `ConvergenceResult` with sensible defaults |
| `grouped_result` | `GroupedConvergenceResult` with two groups (`group` = a/b) |

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
| `test_sample_frame_filter_cols` | Required `it_col` and `target_col` are present |
| `test_sample_frame_group_cols_str_normalized` | A string `group_cols` is normalized to a one-element list |
| `test_sample_frame_group_cols_list_preserved` | A list of group columns is preserved as a list |
| `test_sample_frame_group_cols_none_becomes_empty` | `None` group_cols is normalized to an empty list |
| `test_sample_frame_group_cols_auto_it_per_group` | Auto-created `it` restarts at 1 within each group |
| `test_sample_frame_group_col_missing_raises` | ColumnNotFoundError when a group column is absent |
| `test_sample_frame_group_col_unsupported_dtype_raises` | TypeError for an unsupported group column dtype |
| `test_sample_frame_group_cols_frozen` | `group_cols` is immutable after construction |

---

### 3.2 `registry.py` — CriterionRegistry

**File:** `tests/test_registry.py`

| Test | Description |
|------|-------------|
| `test_register_decorator` | `@registry.register()` adds criterion |
| `test_register_programmatic` | `registry.register(instance)` adds criterion |
| `test_register_duplicate_raises` | ValueError on duplicate name |
| `test_register_overwrite_allows_duplicate` | `overwrite=True` replaces existing |
| `test_register_empty_name_raises` | ValueError when `criterion.name` is empty |
| `test_get_existing` | Returns correct criterion instance |
| `test_get_unknown_raises` | ValueError with available names in message |
| `test_names_returns_tuple` | Returns tuple of registered names |
| `test_names_empty_initially` | Empty tuple for fresh registry |
| `test_describe_existing` | `describe()` prints panel and table (capsys) |
| `test_describe_unknown_prints_error` | `describe()` prints error for unknown name |
| `test_registry_is_singleton` | Module-level registry is shared |

---

### 3.3 `result.py` — ConvergenceResult, ResultPlotter & GroupedConvergenceResult

**File:** `tests/test_result.py`

#### 3.3.1 ConvergenceResult

| Test | Description |
|------|-------------|
| `test_result_creation` | Valid `ConvergenceResult` construction |
| `test_result_frozen` | Immutability of dataclass |
| `test_result_diagnostics_default` | `diagnostics` defaults to empty dict |
| `test_result_to_polars` | Returns the data DataFrame |
| `test_result_to_pandas` | Returns pandas DataFrame |
| `test_result_str` | String representation contains the method name |
| `test_result_repr` | Compact repr contains the class name |
| `test_result_summary_converged` | `summary()` prints "Converged" (capsys) |
| `test_result_summary_not_converged` | `summary()` prints "Not Converged" |
| `test_result_summary_with_diagnostics` | Diagnostics appear in summary |
| `test_result_summary_none_estimate` | Handles `None` estimate gracefully |
| `test_convergence_result_getitem_raises` | Ungrouped results are not subscriptable (TypeError) |
| `test_convergence_result_error_by_raises` | Ungrouped results do not support `error_by` (TypeError) |

#### 3.3.2 ResultPlotter

| Test | Description |
|------|-------------|
| `test_result_plotter_creation` | `ResultPlotter` instantiated via `.plot` |
| `test_plotter_evolution_returns_axes` | Returns matplotlib Axes |
| `test_plotter_evolution_missing_cols_raises` | ValueError when required columns missing |
| `test_plotter_evolution_no_convergence` | Plot works when `is_converged` all False |
| `test_plotter_evolution_with_show_false` | Does not call `plt.show()` |

#### 3.3.3 GroupedConvergenceResult

| Test | Description |
|------|-------------|
| `test_grouped_result_is_dict` | `GroupedConvergenceResult` is a dict of group keys |
| `test_grouped_result_len` | Two groups are present |
| `test_grouped_result_n_sum` | `n` aggregates the sample counts of every group |
| `test_grouped_result_error_sum` | `error` is the residual absolute sum across groups |
| `test_grouped_result_error_none_when_all_none` | `error` is `None` when no group exposes an error |
| `test_grouped_result_error_by_single` | `error_by` keeps a single group column |
| `test_grouped_result_error_by_list` | `error_by` accepts a list of group columns |
| `test_grouped_result_error_by_unknown_raises` | ValueError for unknown group columns |
| `test_grouped_result_error_by_collapses` | `error_by` marginalizes over group columns not kept |
| `test_grouped_result_error_by_none_bucket` | A collapsed bucket with no errors maps to `None` |
| `test_grouped_result_estimate_raises` | `estimate` cannot be aggregated (TypeError) |
| `test_grouped_result_diagnostics_raises` | `diagnostics` cannot be aggregated (TypeError) |
| `test_grouped_result_is_converged_all_true` | `is_converged` is True when every group converged |
| `test_grouped_result_is_converged_false_if_any` | `is_converged` is False when any group did not converge |
| `test_grouped_result_data_has_group_column` | Combined data attaches the group columns |
| `test_grouped_result_data_row_count` | Combined data concatenates one row per group |
| `test_grouped_result_to_polars` | `to_polars()` returns a Polars DataFrame |
| `test_grouped_result_to_pandas` | `to_pandas()` returns a pandas DataFrame |
| `test_grouped_result_execution_time_none` | `execution_time_sec` is `None` when unset on every group |
| `test_grouped_result_execution_time_sum` | `execution_time_sec` sums the per-group timings |
| `test_grouped_result_plotter_creation` | `plot` returns a `ResultPlotter` |
| `test_grouped_result_plotter_evolution_raises` | Direct evolution plotting on a grouped result raises TypeError |
| `test_grouped_result_summary_prints_groups` | `summary()` prints one block per group (capsys) |

---

### 3.4 `api.py` — Convergence Facade

**File:** `tests/test_api.py`

| Test | Description |
|------|-------------|
| `test_convergence_call_with_method` | `convergence(samples, method="clt_uni_abs")` |
| `test_convergence_call_unknown_method_raises` | ValueError for unregistered method |
| `test_convergence_getattr_dispatch` | `convergence.clt_uni_abs(samples)` |
| `test_convergence_getattr_unknown_raises` | ValueError for unknown attribute |
| `test_convergence_with_eval_frequency` | `eval_frequency` kwarg reaches the criterion |
| `test_convergence_eval_frequency_unsupported_raises` | Supported eval_frequency path returns a result |
| `test_convergence_params_passed_through` | kwargs become params model fields |
| `test_methods_returns_registered` | `mcc.methods()` returns expected names |
| `test_describe_existing_method` | `mcc.describe("clt_uni_abs")` prints info |
| `test_describe_unknown_method` | `mcc.describe("unknown")` prints error |
| `test_samples_returns_sample_frame` | `mcc.samples()` returns `SampleFrame` |
| `test_samples_passes_columns` | `target_col` and `it_col` forwarded correctly |
| `test_samples_passes_group_cols` | `group_cols` is forwarded to the `SampleFrame` |
| `test_convergence_grouped_returns_grouped_result` | Grouped samples produce a `GroupedConvergenceResult` |
| `test_convergence_grouped_execution_time_set` | Execution time is recorded for every group |

---

### 3.5 Not implemented — no wrappers module

The `wrappers.py` module and `tests/test_wrappers.py` are not part of the
current implementation. Eval-frequency functionality is natively supported
within each criterion.

---

### 3.6 `methods/clt_uni_abs.py` — CLTAbsoluteCriterion

**File:** `tests/methods/test_clt_uni_abs.py`

| Test | Description |
|------|-------------|
| `test_clt_params_threshold_required` | `threshold` is required (no default) |
| `test_clt_params_threshold_must_be_positive` | ValidationError on `threshold <= 0` |
| `test_clt_params_confidence_range` | ValidationError on confidence outside (0,1) |
| `test_clt_criterion_registered` | Appears in registry after import |
| `test_clt_run_returns_result` | Returns `ConvergenceResult` instance |
| `test_clt_run_estimate_correct` | Estimate matches expected mean |
| `test_clt_run_n_correct` | `n` matches DataFrame row count |
| `test_clt_run_error_correct` | Error is reported (absolute CLT error) |
| `test_clt_run_converged_true` | Converges with a loose threshold |
| `test_clt_run_converged_false` | Does not converge with strict threshold on high-variance data |
| `test_clt_run_diagnostics` | Diagnostics contain threshold, confidence_level, z_score |
| `test_clt_run_data_columns` | Output DataFrame has the 6 expected columns |
| `test_clt_run_zero_variance` | Handles constant target (`std=0`) via `sample_frame_constant` |
| `test_clt_run_warmup_warns` | Warns when fewer than 30 samples (warm-up) are available |
| `test_clt_run_warmup_not_converged` | The warm-up path returns a not-converged result |
| `test_clt_run_warmup_estimate_none` | The warm-up path exposes no estimate |
| `test_clt_run_warmup_empty_data` | The warm-up path returns an empty diagnostic frame |
| `test_clt_run_large_sample` | Converges with large low-variance sample |
| `test_clt_assumptions_non_empty` | Assumptions tuple is populated |
| `test_clt_assumptions_sample_large_enough` | Sample size assumption references 30 |
| `test_clt_limitations_non_empty` | Limitations tuple is populated |
| `test_clt_references_non_empty` | References tuple is populated |
| `test_clt_grouped_returns_grouped_result` | Grouped input yields a `GroupedConvergenceResult` |
| `test_clt_grouped_keys` | Grouped keys map the group column to its values |
| `test_clt_grouped_per_group_n` | Each group reports its own sample count |
| `test_clt_grouped_error_by` | `error_by` keeps the requested group column |
| `test_clt_grouped_multi_error_by` | `error_by` marginalizes over the un-kept group column |

---

### 3.7 `methods/clt_uni_rel.py` — CLTRelativeCriterion

**File:** `tests/methods/test_clt_uni_rel.py`

| Test | Description |
|------|-------------|
| `test_clt_rel_params_threshold_required` | `threshold` is required (no default) |
| `test_clt_rel_params_threshold_must_be_positive` | ValidationError on `threshold <= 0` |
| `test_clt_rel_params_confidence_range` | ValidationError on confidence outside (0,1) |
| `test_clt_rel_criterion_registered` | Appears in registry after import |
| `test_clt_rel_run_returns_result` | Returns `ConvergenceResult` instance |
| `test_clt_rel_run_estimate_correct` | Estimate matches expected mean |
| `test_clt_rel_run_n_correct` | `n` matches DataFrame row count |
| `test_clt_rel_run_error_correct` | Error matches `abs_error / abs(mean)` |
| `test_clt_rel_run_error_col_is_rel_error` | The reported error column is `rel_error` |
| `test_clt_rel_run_converged_true` | Converges with a loose threshold on zero-variance data |
| `test_clt_rel_run_converged_false` | Does not converge with strict threshold on high-variance data |
| `test_clt_rel_run_diagnostics` | Diagnostics contain threshold, confidence_level, z_score, relative_error_used |
| `test_clt_rel_run_data_columns` | Output DataFrame has the 7 expected columns |
| `test_clt_rel_run_zero_variance` | Handles constant target (`std=0`) |
| `test_clt_rel_run_near_zero_mean_fallback` | Falls back to absolute error when the estimate is near zero |
| `test_clt_rel_run_near_zero_mean_error_is_abs_error` | Returned error equals the absolute error when falling back |
| `test_clt_rel_run_near_zero_mean_rel_error_is_null` | Relative error column is null when the estimate is near zero |
| `test_clt_rel_run_large_sample` | Converges with large low-variance sample |
| `test_clt_rel_run_insufficient_sample_warns` | Warns when fewer than 30 samples are available |
| `test_clt_rel_run_insufficient_sample_not_converged` | The insufficient-sample warm-up path is not converged |
| `test_clt_rel_run_with_eval_frequency` | `eval_frequency` produces a periodic diagnostic frame |
| `test_clt_rel_run_eval_frequency_last_row_is_total` | The final evaluated row corresponds to the full sample |
| `test_clt_rel_run_eval_frequency_diagnostics` | `eval_frequency` diagnostics report frequency and evaluations |
| `test_clt_rel_run_eval_frequency_has_rel_error_column` | The periodic frame still exposes `rel_error` |
| `test_clt_rel_grouped_returns_grouped_result` | Grouped input yields a `GroupedConvergenceResult` |
| `test_clt_rel_grouped_keys` | Grouped keys map the group column to its values |
| `test_clt_rel_grouped_per_group_n` | Each group reports its own sample count |
| `test_clt_rel_grouped_error_by` | `error_by` keeps the requested group column |
| `test_clt_assumptions_non_empty` | Assumptions tuple is populated |
| `test_clt_assumptions_sample_large_enough` | Sample size assumption references 30 |
| `test_clt_limitations_non_empty` | Limitations tuple is populated |
| `test_clt_references_non_empty` | References tuple is populated |

---

## 4. Edge Cases & Error Handling

Covered across the module test files:

- Empty DataFrames (`test_sample_frame_empty_df_raises`)
- Single-row / small DataFrames (warm-up `< 30` warning path)
- All-identical values / zero variance (`sample_frame_constant`)
- Near-zero estimates (relative criterion fallback to absolute error)
- Missing and unsupported group columns
- Invalid parameters (`threshold`, `confidence_level`)
- Missing target / iteration / group columns
- Null / NaN / Inf target values

---

## 5. Integration Tests

**File:** `tests/test_integration.py`

| Test | Description |
|------|-------------|
| `test_full_pipeline_clt_uni_abs` | samples -> convergence -> result -> summary |
| `test_full_pipeline_with_eval_frequency` | Full pipeline with eval_frequency |
| `test_method_discovery_flow` | methods() -> describe() -> convergence() |
| `test_result_export_polars` | `to_polars()` returns valid DataFrame |
| `test_result_export_pandas` | `to_pandas()` returns valid DataFrame |
| `test_result_plotting_pipeline` | `result.plot.evolution()` produces axes |
| `test_full_pipeline_grouped` | Grouped samples flow through convergence into per-group results |
| `test_full_pipeline_grouped_indexing` | A specific group can be indexed from the grouped result |

---

## 6. Benchmarks

**File:** `benchmarks/test_eval_frequency_comp.py`

Run with:

```bash
uv run pytest benchmarks/ --benchmark-json=benchmarks/results.json
```

| Benchmark | Description |
|-----------|-------------|
| `test_bench_eval_frequency_scaling` | Scaling of eval_frequency by `n_samples` (100 / 1k / 10k), `eval_freq` (1 / 10 / 100) and `implementation` |
| `test_bench_grouped_scaling` | Scaling with `group_cols` across `n_groups` (1 / 10 / 100) for `clt_uni_abs` and `clt_uni_rel` |

`benchmarks/compare.py` reads `results.json`; it currently assumes the
`n_samples` / `eval_freq` / `implementation` parameters and may need updating
to handle the grouped dimension.

---

## 7. Coverage Strategy

### 7.1 Running Coverage

Informative, not mandatory to reach a goal. However, warn the user when the
desired coverage by module is not met:

```bash
uv run pytest --cov=mocaco --cov-report=term-missing --cov-report=html
```

### 7.2 Desired Coverage by Module

| Module | Target |
|--------|--------|
| protocols.py | 80% |
| registry.py | 60% |
| result.py | 80% |
| api.py | 80% |
| methods/clt_uni_abs.py | 80% |
| methods/clt_uni_rel.py | 80% |
| **Overall** | **>= 70%** |

### 7.3 Known Coverage Gaps (acceptable)

- `plt.show()` interactive display (backend switched to `Agg`; not asserted)
- Rich console formatting edge cases (visual only)
- `generate_stubs.py` script (not part of package)
- The pre-existing `native2` benchmark case references a removed criterion
  (`clt_uni_abs2`) and currently fails; benchmark-only, not part of the test
  suite.

---

## 8. Execution Order

1. `conftest.py` — shared fixtures
2. `test_protocols.py` — foundational data structure
3. `test_registry.py` — method registration
4. `test_result.py` — result representation (`ConvergenceResult`, `ResultPlotter`, `GroupedConvergenceResult`)
5. `methods/test_clt_uni_abs.py` — absolute criterion logic
6. `methods/test_clt_uni_rel.py` — relative criterion logic
7. `test_api.py` — public API facade
8. `test_integration.py` — end-to-end flows

---

## 9. Quality Gates

After each modification run:

```bash
uv run pytest tests/
uv run ruff check --fix . && uv run ruff format .
uv run mypy src/
```

Expected: all tests pass, "All checks passed!", "Success: no issues found".
