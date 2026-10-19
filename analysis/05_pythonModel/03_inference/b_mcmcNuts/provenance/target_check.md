result: results/target_check.tsv
script: scripts/check_target.py
        sha256:2f944d15244bbbd6adc1b4b80e074336791186f917351d1995655e9e18430d20
        scripts/mcmc_nuts.py
        sha256:c4d5f6dd51c05a9efc400125abaea28aec80eced26ed8f6a321550b08c704cb4
        ../../scripts/chapkit_ewars_python/ewars_python/frame.py
        sha256:7b593a88a125bd95595f86b2bb82756b19184b80950f7ba12f50d04cdebe8f36
        ../../scripts/chapkit_ewars_python/ewars_python/latent.py
        sha256:d9763fdc950c359b818db315c2933b6f0a8c9de9165e368f547afc0a27103ef2
        ../../scripts/chapkit_ewars_python/ewars_python/laplace.py
        sha256:a1d5bf8e8c2554f1c47b5910608aad5ba5c8f383d31e1fe4c8ffe0eab8b09252
        ../../scripts/chapkit_ewars_python/ewars_python/primitives.py
        sha256:df963e55c1b5e056c1e5106981422532d9c68d3b991ad6f969dc4ea61ceef1ab
        ../../scripts/chapkit_ewars_python/ewars_python/inla_approx.py
        sha256:e02c317aa9158a7fc8b58b831aa7dec2b69bd3040fed219cc0af1d43cbf4f196
invocation: run.sh step 1: $PYTHON scripts/check_target.py ../../../03_referenceHarness/results ../../../03_referenceHarness/scripts/configs ../../scripts/chapkit_ewars_python results/target_check.tsv > results/check_target.log
inputs:
  ../../../03_referenceHarness/results/inputs  dir-sha256:67c487cbca941566
  ../../../03_referenceHarness/scripts/configs  dir-sha256:ebfb3d4b4f037dde
environment: environment/ (project main; numpyro 0.22.0, jax/jaxlib 0.11.2 added in batch 9)
seeds: 20261018, fixed in the script, draws the 20 test points per dataset x variant x parametrisation; no result depends on its value
commit: 291b702
instructions-commit: 400536d
node: analysis/05_pythonModel/03_inference/b_mcmcNuts
produced: 2026-10-20
alternatives-considered: checking at posterior draws rather than random points (random points over a wide theta range test the identity where the posterior has no mass too, which is the stronger check); an exact-Gaussian normalising constant (JC-32: then (a) and (b) would target different densities)
agency: agent-autonomous
information: -
files:
  results/target_check.tsv
  results/check_target.log
