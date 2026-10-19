result: (5 files, listed under files:)
script: scripts/compare.py
        sha256:b2cb6d3ddbf2fcb1265a3edbe538e1095501c116263816ef445e10b3f9ef20fd
        ../../../04_fidelityMetrics/scripts/fidelity.py
        sha256:322524a62c7397ade5b5b574ba84d406c43ec010bb6cef10b79c3285d0838445
invocation: run.sh step 3: $PYTHON scripts/compare.py results/mcmc_fits/fits ../a_laplaceCcd/results/python_fits/fits ../../../03_referenceHarness/results ../../../04_fidelityMetrics/scripts ../../../04_fidelityMetrics/results/r_fit_health.tsv results > results/compare.log
inputs:
  results/mcmc_fits/fits  dir-sha256:d9b96c9c2386cbdb
  ../a_laplaceCcd/results/python_fits/fits  dir-sha256:7d4c0f011dcf4adc
  ../../../03_referenceHarness/results/fits  dir-sha256:a2e762fb1afdc721
  ../../../04_fidelityMetrics/results/r_fit_health.tsv  sha256:e438667444b7320d
environment: environment/ (project main; numpyro 0.22.0, jax/jaxlib 0.11.2 added in batch 9)
seeds: none (deterministic)
commit: 291b702
instructions-commit: 400536d
node: analysis/05_pythonModel/03_inference/b_mcmcNuts
produced: 2026-10-20
alternatives-considered: JC-25 (measures, reused unchanged). Every R run kept, each pair labelled by the R run's health (plan §4b, 2026-10-17). Candidate (a)'s committed fits read as an input rather than re-run, so that (b) is compared with the (a) that the closeness report and the service rest on
agency: agent-autonomous
information: -
files:
  results/l3_mcmc_pairs.tsv
  results/l3_mcmc_quantities.tsv.gz
  results/l4_mcmc_pairs.tsv
  results/l4_mcmc_rows.tsv.gz
  results/compare.log
