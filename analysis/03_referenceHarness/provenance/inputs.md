result: results/inputs/monthly_ewars/future.csv
        results/inputs/monthly_ewars/historic.csv
        results/inputs/weekly_nicaragua/future.csv
        results/inputs/weekly_nicaragua/historic.csv
script: scripts/make_fit_inputs.py
        sha256:78d6a2aba387c0990ca636b2ee3d29452e2dfb5e0d8bef87aa53156774a0979c
invocation: step 2 of run.sh: $PYTHON scripts/make_fit_inputs.py ../01_referenceThroughChap/results/run1/inputs ../01_referenceThroughChap/results/run1/weekly_workspace/workspace/historic.csv 3 results/inputs
inputs: ../01_referenceThroughChap/results/run1/inputs/monthly_ewars.csv sha256:da7deebee0779d15ed8240229578564d86151539b8758f58557201535d786e5c
  ../01_referenceThroughChap/results/run1/inputs/weekly_nicaragua.csv sha256:c72c40fe12d4436f162e186e4ada906b94d10e8eb712764efc2aea0c19c54513
  ../01_referenceThroughChap/results/run1/weekly_workspace/workspace/historic.csv sha256:202993dd8e87689acd0de996dbfac1ba3043b3194b67783b6069f621ae4c4900 (the check)
environment: environment/ (project main)
seeds: none (deterministic)
commit: de28ef4 (scripts as committed before the run); eb47134 (the same script contents, plus the
  diagnostic and summariser changes, committed after they ran — see each record)
instructions-commit: 400536d
node: analysis/03_referenceHarness
produced: 2026-10-15
alternatives-considered: (a) chap's climatology covariates for the future window, as in the backtest. Rejected: R and Python see identical inputs either way, and observed covariates keep a weather model out of the harness (JC-14). (b) several windows per dataset. Rejected for cost: one window x 4 variants x 5 replicates already spans the config space the plan names; the chap repeats cover the 7 backtest windows.
agency: agent-autonomous
information: agent-retrieved (chap's file shape read from its workspace in node 01)
