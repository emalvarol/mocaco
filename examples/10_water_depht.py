"""
Example with real data. External water depht around buildings.

On this case we use data comming from a flood model. Data contains external watter depht values
in meters(he) from multiple random monte carlo iterations (SN) across different scenarios
(return periods, RP) and for multiples buildings (BID).

The objective is to reach convergence on each individual building and each scenario. The convergence
criterion threshold is an absolut 0.1 m (we know the terrain error is around that value and the flood
model - HEC-RAS - execution is time consuming so we conclude it as a good criterion). Mocaco can
achieve this in a three lines using the clt_uni_abs criterion.
"""

import polars as pl

import mocaco as mcc

# 1. Open example csv file as polar dataframe
df = pl.read_csv(r"examples\data\water_depht_samples.csv")

# 2. Freeze into a SampleFrame (validates inputs)
samples = mcc.samples(df, it_col="SN", target_col="he", group_cols=["RP", "BID"])

# 3. Run a criterion
result = mcc.convergence.clt_uni_abs(samples, threshold=0.1, eval_frequency=50)

# 4. Print basic results and data
# Since we used `group_cols` the return is a `GroupedConvergenceResult` class.
# This means we can access to some general results.
# Between them the is_convergence complete our objective:
print(f"Have all BID x RP combinations converged? -> {result.is_converged}")
print(f"{result.n} rows processed in {result.execution_time_sec}s")
print("The sum of the error across each BID differenciating by RP is")
print(result.error_by(keep=["RP"]))
print("""The sum of the residual error (only those BID whose error is above the threshold)
    across each BID differenciating by RP is""")
print(result.residual_error_by(keep=["RP"]))
print(result.data)
# We can also acces to individual resuls, for example:
print(result[{"RP": 500, "BID": 1997}].estimate)

# 5. Plot convergence charts if desired
# We can plot individual chart:
with pl.Config(tbl_rows=-1):
    print(result[{"RP": 500, "BID": 1997}].data)
ax = result[{"RP": 500, "BID": 1997}].plot.evolution(show=True)
# Or the residual error evolution across all BID for each RP
ax = result.plot.residual_error_evolution(show=True, keep=["RP"])

# EXTRA:
# Everything could be collapsed in just one call
assert mcc.convergence.clt_uni_abs(
    mcc.samples(df, it_col="SN", target_col="he", group_cols=["RP", "BID"]),
    threshold=0.1,
    eval_frequency=50,
).is_converged
