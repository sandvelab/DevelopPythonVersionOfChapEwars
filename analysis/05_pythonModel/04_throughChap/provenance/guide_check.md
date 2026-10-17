result: (4 files, listed under files:)
script: scripts/verify_guide.sh
        sha256:52bbf770f287859c34629066aa364db741efd8965e457ead6ddd5df039b24743
        ../scripts/chapkit_ewars_python/README.md
        sha256:7bb0a1ca1947690fdc1b9758b6d6e3f22773bc0992d99233a4e474d127b088b3
invocation: run.sh step 4: bash scripts/verify_guide.sh ../scripts/chapkit_ewars_python/README.md results/guide_check
inputs:
environment: a fresh shell (env -i) with uv, git, docker and curl; the guide installs what it needs
seeds: the guide's evaluation uses the derived seed (JC-24); its CRPS, 21.9456264, equals run1's in results/l5_evaluations.tsv
commit: 618c4b3 (scripts); verify_guide.sh and the README as hashed above were added to run.sh while the run was in progress and are committed after it
instructions-commit: 400536d
node: analysis/05_pythonModel/04_throughChap
produced: 2026-10-17
alternatives-considered: Checking the native uvicorn route as well: the README marks that line as not run by the check
agency: agent-autonomous
information: -
files:
  results/guide_check/guide_commands.sh
  results/guide_check/guide_exit_code.txt
  results/guide_check/guide_run.log
  results/guide_check/guide_sha256.txt
