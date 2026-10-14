result: results/inla_defaults.tsv
script: scripts/inla_defaults.R
        sha256:40fbab0410792c9bd2fbf22c9100fa89147cba07eddc9a0443295fe078f9a293
invocation: step 2 of run.sh: docker run ... <reference image> /s/inla_defaults.R /out/inla_defaults.tsv
inputs: the installed INLA 25.10.19 in the reference image (inla.models(), control defaults, getOption, formals);
  the "set by predict.R" rows are transcribed from Archive/chapkit_ewars_model/src/scripts/predict.R:192-197
  (sha256:37bdeb850ca786924cb9f27e999b574b2eb9a46627c27b421023183ca250bad4)
environment: node env/ (the reference image)
seeds: none (deterministic)
commit: b534c59
instructions-commit: 400536d
node: analysis/02_translationInventory
produced: 2026-10-14
alternatives-considered: reading the defaults from INLA's online documentation (inla.doc). Rejected: the
  documentation is not versioned with the package, and the image ships none; the installed package is
  what the reference ran. The archived .tex at tag Version_25.10.19 is kept as the explanatory text.
agency: agent-autonomous
information: agent-retrieved
