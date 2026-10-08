# Polars Integration Patterns

mocaco is built around [Polars](https://pola.rs/) for fast, memory-efficient data processing. The library ensures data integrity by normalizing inputs into a read-only `SampleFrame` before applying convergence logic and output a consistent result for safety unpack.

## The `SampleFrame` Validator

To prevent accidental modification and guarantee structural integrity, mocaco uses the `mcc.samples()` function. This function strictly requires the target column to be numeric and free of missing (Null), NaN, or Infinite values. If the iteration column (`it_col`) is omitted, mocaco automatically creates an `it` column with sequential indices.

## Retrieving Results

Once a convergence method runs, it returns a `ConvergenceResult` object. You can extract the full diagnostic history back into a Polars DataFrame using `result.to_polars()` or directly via the `result.data` attribute. This allows for seamless downstream analysis or custom plotting.

*See `examples/01_polars_integration.py` for a runnable example.*