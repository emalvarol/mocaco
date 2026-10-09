"""Noise vs smooth convergence: eval_frequency."""

import numpy as np
import polars as pl

import mocaco as mcc

# 1. Generate noisy Monte Carlo samples
np.random.seed(42)
n_samples = 5000
true_value = 5.0
noise = np.random.normal(0, 2.0, n_samples)
samples_array = true_value + noise

df = pl.DataFrame({"it": range(1, n_samples + 1), "value": samples_array})
samples = mcc.samples(df, it_col="it", target_col="value")

# 2. Run criterion using eval_frequency to smooth checks
# Instead of checking 5000 times, we evaluate every 100 iterations.
result = mcc.convergence.clt_absolute(samples, threshold=0.1, eval_frequency=100)

result.summary()

# 3. Plot the convergence evolution
# This requires matplotlib to be installed
result.plot.evolution(show=True)
