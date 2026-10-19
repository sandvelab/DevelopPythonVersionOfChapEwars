result: (5 files, listed under files:)
script: scripts/summarise.py
        sha256:ea1d74106f81383c5cfd8ae63e01c20c8511da037ff208039276fee2899419de
invocation: run.sh step 4: $PYTHON scripts/summarise.py results ../a_laplaceCcd/results/python_fits/python_fits_timings.tsv > results/summarise.log
inputs:
  results/l3_mcmc_pairs.tsv  sha256:7db42ba752a8b0ff
  results/l3_mcmc_quantities.tsv.gz  sha256:d3cea19db1febed1
  results/l4_mcmc_pairs.tsv  sha256:e0a506a4ee9391a5
  results/mcmc_fits/mcmc_fits_summary.tsv  sha256:989044e1d552dcfd
  ../a_laplaceCcd/results/python_fits/python_fits_timings.tsv  sha256:ef60e6e90aef3654
environment: environment/ (project main)
seeds: none (deterministic)
commit: 291b702 (summarise.py itself was written after this commit, ran uncommitted, and is committed unchanged in the after-run commit; its digest above is the file that ran)
instructions-commit: 400536d
node: analysis/05_pythonModel/03_inference/b_mcmcNuts
produced: 2026-10-20
alternatives-considered: summaries over clean R fits only; the flagged R fit's pairs stay in l3/l4_mcmc_pairs.tsv, as in 04_fidelityMetrics. Medians over pairs of per-pair medians, as the closeness report summarises candidate (a)
agency: agent-autonomous
information: -
files:
  results/summary_l3.tsv
  results/summary_hyperparameters.tsv
  results/summary_l4.tsv
  results/summary_cost.tsv
  results/summarise.log
