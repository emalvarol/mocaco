# clt_absolute

Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `threshold` | `<class 'float'>` | *required* | Maximum accepted absolute Monte Carlo error. |
| `confidence_level` | `<class 'float'>` | `0.95` | Confidence level used for the CLT margin of error. |
| `stb_window` | `<class 'int'>` | `30` | Minimum number of consecutive iterations meeting the threshold. |

## Assumptions

- Samples are independent and identically distributed (i.i.d.).
- The target quantity has finite variance.
- The sample size is sufficiently large for the CLT to provide a normal approximation.

## Limitations

- This is a probabilistic stopping criterion, not a proof of convergence.
- For small sample sizes, the normal approximation may be inaccurate.
- Does not detect systematic bias or non-stationarity in the sampling process.
- The stability window introduces a lag in detecting convergence.

## Result Interpretation

is_converged is True when the CLT-based absolute error has stayed below the threshold for at least stb_window consecutive iterations. estimate is the cumulative mean at the final sample. error is the CLT-based absolute error (z_score * SEM) at the final sample. n is the total number of samples evaluated.

## Example Usage

```python
import polars as pl
import mocaco as mcc

df = pl.DataFrame({"it": range(100), "value": [1.0] * 100})
samples = mcc.samples(df, it_col="it", target_col="value")
result = mcc.convergence.clt_absolute(samples, threshold=0.1)
print(result.is_converged)
```

## References

- Robert, C.P. and Casella, G. (2004). Monte Carlo Statistical Methods (2nd ed.). Springer.
- Asmussen, S. and Glynn, P.W. (2007). Stochastic Simulation: Algorithms and Analysis. Springer.
