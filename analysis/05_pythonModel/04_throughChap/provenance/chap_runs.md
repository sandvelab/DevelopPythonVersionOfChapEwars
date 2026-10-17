result: (14 files, listed under files:)
script: scripts/run_python_through_chap.sh
        sha256:8f4f168c1102d3d06e63966320dd0c6bfb73032b8666de69b9682dc9234b038f
        ../../04_fidelityMetrics/scripts/ensure_chap_core.sh
        sha256:e70d0939a800d705a6b8d4f6995a1151a1e844ce009a98526102bbf5ff813772
        ../scripts/chapkit_ewars_python/main.py
        sha256:20b37fd5b2417c2eaceaee0b03c60f176cfd514a836d44836b16e22ae4ac83a2
        ../scripts/chapkit_ewars_python/Dockerfile
        sha256:07687b5a1db7504736f8e0d29f0a43832edec9ee4d3b87a4bcdd8b2c1a6388ad
        ../scripts/chapkit_ewars_python/uv.lock
        sha256:760a265d74efc19b5cb301f32cc8db6c022e2af4704c4fa14bfe8332d2ad7015
        ../scripts/chapkit_ewars_python/scripts/predict.py
        sha256:21d93566c517d413ae67b0028d11eeaef6a5c53a940caed4f7502a81d62b3e9c
        ../scripts/chapkit_ewars_python/ewars_python/model.py
        sha256:d2e1aa970f894b913ec127f2198d4786925bbf2da2692d5646beb4c22ab64f1c
        ../scripts/chapkit_ewars_python/ewars_python/inla_approx.py
        sha256:e02c317aa9158a7fc8b58b831aa7dec2b69bd3040fed219cc0af1d43cbf4f196
        ../scripts/chapkit_ewars_python/ewars_python/laplace.py
        sha256:a1d5bf8e8c2554f1c47b5910608aad5ba5c8f383d31e1fe4c8ffe0eab8b09252
        ../scripts/chapkit_ewars_python/ewars_python/latent.py
        sha256:d9763fdc950c359b818db315c2933b6f0a8c9de9165e368f547afc0a27103ef2
        ../scripts/chapkit_ewars_python/ewars_python/frame.py
        sha256:7b593a88a125bd95595f86b2bb82756b19184b80950f7ba12f50d04cdebe8f36
        ../scripts/chapkit_ewars_python/ewars_python/primitives.py
        sha256:17161aba104db63a7d2999c4c7efcee505015854221f4eef20ad3c286713c829
invocation: run.sh step 1: env -i ... bash --noprofile --norc scripts/run_python_through_chap.sh 3 results/chap_runs work (tee results/chap_runs/run.log)
inputs:
  ../../01_referenceThroughChap/results/run1/inputs  dir-sha256:c506346e1754d5ad
  ../../01_referenceThroughChap/scripts/ewars_config.yaml  sha256:db6143456deba365
  ../../01_referenceThroughChap/scripts/backtest_settings.env  sha256:c890f99e011effeb
environment: chap-core b8c8f788 from its uv.lock; the Python service image built from ../scripts/chapkit_ewars_python at commit 618c4b3 (results/chap_runs/image_id.txt); claim.md, Environment
seeds: run1: the derived seed per split's inputs (JC-24); run2, run3: EWARS_SEED = rule of readme-at-start.md on 'python-through-chap/run<r>' (1644915050, 1175527052; results/chap_runs/timings.tsv)
commit: 618c4b3
instructions-commit: 400536d
node: analysis/05_pythonModel/04_throughChap
produced: 2026-10-17
alternatives-considered: Running the service natively (uvicorn) instead of in Docker: chap would drive it the same way; Docker matches how the R original is evaluated (plan §4, Environment). More runs: each costs about 7 minutes and the per-row spread is already at the R-vs-R level
agency: agent-autonomous
information: -
files:
  results/chap_runs/chap_core_commit.txt
  results/chap_runs/eval/monthly_ewars__ewars_python__run1.nc
  results/chap_runs/eval/monthly_ewars__ewars_python__run2.nc
  results/chap_runs/eval/monthly_ewars__ewars_python__run3.nc
  results/chap_runs/eval/weekly_nicaragua__ewars_python__run1.nc
  results/chap_runs/eval/weekly_nicaragua__ewars_python__run2.nc
  results/chap_runs/eval/weekly_nicaragua__ewars_python__run3.nc
  results/chap_runs/image_id.txt
  results/chap_runs/run.log
  results/chap_runs/service_container_run1.log
  results/chap_runs/service_container_run2.log
  results/chap_runs/service_container_run3.log
  results/chap_runs/service_info.json
  results/chap_runs/timings.tsv

## 2026-10-17 — primitives.py changed after this run (comment only)
A docstring line was added stating that it draws no random numbers (the seeds check had
matched the words "random walk"). No code changed; nothing was re-run on it.
script: ../scripts/chapkit_ewars_python/ewars_python/primitives.py
        sha256:df963e55c1b5e056c1e5106981422532d9c68d3b991ad6f969dc4ea61ceef1ab
