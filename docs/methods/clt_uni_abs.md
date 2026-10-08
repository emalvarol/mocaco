# clt_uni_abs

Central Limit Theorem based convergence criterion using an absolute Monte Carlo error threshold.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `threshold` | `float` | *required* | Maximum accepted absolute Monte Carlo error. |
| `confidence_level` | `float` | `0.95` | Confidence level used for the CLT margin of error. |
| `eval_frequency` | `int | None` | `None` | Step interval for periodic evaluation of convergence history natively in Polars. |

## Assumptions

- Samples are independent and identically distributed (i.i.d.).
- The target quantity has finite variance.
- The sample size is sufficiently large for the CLT to provide a normal approximation. The deafult stb_window = 30 aims to support this assumption.

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

- https://en.wikipedia.org/wiki/Central_limit_theorem
