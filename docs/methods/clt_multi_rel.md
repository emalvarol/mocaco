# clt_multi_rel

Multivariate Central Limit Theorem based convergence criterion using a relative confidence-region volume tolerance (Vats et al., 2019).

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alpha` | `float` | `0.05` | Significance level of the Hotelling F-based confidence region that builds the left-hand side of the rule (the confidence-region radius, i.e. the error). The confidence level is 1 - alpha. |
| `epsilon` | `float` | `0.05` | Relative tolerance applied to the natural scale of the target distribution, det(cov)^(1/(2p)). It defines the threshold rhs = epsilon * det(cov)^(1/(2p)); convergence requires the confidence-region radius (error) to fall below it. |
| `eval_frequency` | `int | None` | `None` | Step interval (in iterations) between convergence checkpoints. If None, the criterion is evaluated once at the final sample. |
| `warm_up_period` | `int` | `100` | Warm-up sample size (n*) before which convergence is never declared and at which the first checkpoint is taken. |

## Assumptions

- Samples are independent and identically distributed (i.i.d.).
- The vector target quantity has finite second moments and a positive-definite covariance matrix.
- The sample size reaches the warm-up period (default 100) for the multivariate CLT to hold.
- At least two target columns are provided and they are not perfectly collinear.

## Limitations

- This is a probabilistic stopping criterion, not a proof of convergence.
- Requires n > p effective dimensions for the sample covariance to be invertible.
- When the covariance is degenerate (fewer than two varying columns, n <= p, or a non-positive determinant) the error, threshold and residual are reported as 0 and count as convergence at that checkpoint (still gated by the warm-up period).
- The threshold (epsilon * det^(1/(2p))) depends on n; a single final value is stored in diagnostics, so the module-level residual evolution is asymptotic (exact at the last checkpoint).
- No scalar target estimate is produced; estimate is the natural scale det^(1/(2p)) and the estimate +/- error band from plot.evolution is not physically meaningful here.
- Does not detect systematic bias or non-stationarity in the sampling process.

## Result Interpretation

is_converged is True when, at the last checkpoint with n >= warm_up_period, the error (confidence-region radius) is at or below the threshold (epsilon * natural scale), i.e. residual == 0. estimate is the natural scale det^(1/(2p)) of the target. error is the confidence-region radius. threshold is the relative tolerance. residual_error is max(0, error - threshold) at the final checkpoint. n is the final checkpoint iteration. data holds the estimate, error, non_conv_count and is_converged evolution across checkpoints.

## Example Usage

```python
import polars as pl
import mocaco as mcc

df = pl.DataFrame(
    {
        "it": list(range(200)) * 1,
        "a": [float(i % 7) for i in range(200)],
        "b": [float((i * 2) % 11) for i in range(200)],
    }
)
samples = mcc.samples(df, it_col="it", target_col=["a", "b"])
result = mcc.convergence.clt_multi_rel(samples)
print(result.is_converged)
```

## References

- Vats, D., Flegal, J. M., & Jones, G. L. (2019). Multivariate output analysis for Markov chain Monte Carlo. Biometrika, 106(2), 321-337. https://doi.org/10.1093/biomet/asz002
