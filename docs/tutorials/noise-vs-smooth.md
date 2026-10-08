# Noise vs Smooth Convergence

Monte Carlo simulations are inherently noisy. Evaluating a stopping criterion on every single sample is computationally inefficient and can trigger false convergence due to localized variance.

## The `eval_frequency` Wrapper

As one of the ways to solve this, mocaco provides a built-in `eval_frequency` wrapper. By passing `eval_frequency=N` into any convergence method, the criterion is evaluated in cumulative chunks (every `N` rows) rather than row-by-row. The diagnostic DataFrames from each evaluation are automatically concatenated.

## Visualizing Evolution

You can inspect this behavior using the `ConvergenceResult` built-in plotting capability. Calling `result.plot.evolution(show=True)` renders a Matplotlib plot showing the estimate, the error band, and a vertical dashed line at the exact iteration where `is_converged` became true. Alternativelly you can use `result.to_polars()` to inspect the raw result.

*See `examples/02_noise_vs_smooth.py` for a runnable example.*
