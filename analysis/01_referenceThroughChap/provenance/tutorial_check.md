result: results/tutorial_check/tutorial_commands.sh
        results/tutorial_check/tutorial_exit_code.txt
        results/tutorial_check/tutorial_metrics.csv
        results/tutorial_check/tutorial_run.log
        results/tutorial_check/verdict.txt
        results/tutorial_check.log
script: scripts/verify_tutorial.sh
        sha256:a9c992a3eb6e6cc99f8b04d279e91c9372a38e10c076ebd77bfc4e85fcdcce87
        scripts/compare_tutorial_run.py
        sha256:1687cf4a32b8b848bc080feca8048bb56f79992d3e075c17234cd932ce60dd18
invocation: step 3 of this node's run.sh:
  env -i ... bash --noprofile --norc scripts/verify_tutorial.sh
    AI-generated/26-10-14_tutorialRunOriginalEwarsThroughChap.md results/tutorial_check work/tutorial_check
    results/run1 2>&1 | tee results/tutorial_check.log
inputs: ../../AI-generated/26-10-14_tutorialRunOriginalEwarsThroughChap.md  sha256:ce8b75d47be56dc81d8c31971599b541fd34e1c91c6c6e541806f01a0317e2f7
        results/run1/inputs/monthly_ewars.csv, results/run1/metrics/monthly_ewars_metrics.csv (the comparison target)
environment: node env/ (chap-core b8c8f788 from its uv.lock, Python 3.13; EWARS image sha256:959fb4f0…c6ff88, linux/amd64 under emulation on Docker 27.4.0, darwin arm64); the tutorial installs its own copy of the same chap-core commit and lockfile
seeds: none settable (CH-10); the EWARS CRPS of the two runs differs for that reason and is printed as INFO
commit: 687755b
instructions-commit: 400536d
node: analysis/01_referenceThroughChap
produced: 2026-10-14
alternatives-considered: diffing the tutorial's command list against run1's trace only (shows the commands were
  copied, not that they suffice); comparing EWARS scores for equality (impossible while unseeded). The
  deterministic baseline's scores, the byte-identical input and a clean exit together show the tutorial is
  complete and reproduces the reference pipeline.
agency: agent-autonomous
