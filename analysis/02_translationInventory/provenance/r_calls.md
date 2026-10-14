result: results/r_calls.tsv
script: scripts/extract_r_calls.R
        sha256:dbe0cc8c14386d970a043b9b7dcffb71d8744e219177b92f114332dd2fee8cc5
invocation: step 1 of run.sh: docker run --rm --platform linux/amd64 --user root --entrypoint Rscript
  -v scripts:/s:ro -v Archive/chapkit_ewars_model/src/scripts:/src:ro -v results:/out
  <reference image> /s/extract_r_calls.R /src /out/r_calls.tsv
inputs: ../../Archive/chapkit_ewars_model/src/scripts/predict.R  sha256:37bdeb850ca786924cb9f27e999b574b2eb9a46627c27b421023183ca250bad4
        ../../Archive/chapkit_ewars_model/src/scripts/lib.R  sha256:44f65ccdac12137c9f5ee7e0594e5653734070227cc6d3609d02d83005a7510b
        ../../Archive/chapkit_ewars_model/src/scripts/train.R  sha256:1b1b8e37a2a24087e171b056e5d938085bd5fbf981214aebe0da4d581b1c9a77
environment: node env/ (R 4.5.0, INLA 25.10.19, dlnm 2.4.10 in the reference image sha256:959fb4f0…c6ff88)
seeds: none (deterministic)
commit: b534c59
instructions-commit: 400536d
node: analysis/02_translationInventory
produced: 2026-10-14
alternatives-considered: listing the calls by reading the scripts (what batch 1 did for the facts it
  re-verified). Rejected for the inventory: "every R call" is then only as complete as the reading.
  R's parser gives the complete list, and resolving each name with find() after loading the same
  packages gives what supplies it at runtime, masking included. The f() terms inside the formula
  strings are invisible to the parser and are extracted from the string constants instead.
agency: agent-autonomous
