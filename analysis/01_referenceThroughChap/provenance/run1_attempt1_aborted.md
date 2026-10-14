result: results/run1_attempt1_aborted/chap_core_commit.txt
        results/run1_attempt1_aborted/image_digest.txt
        results/run1_attempt1_aborted/run.log
        results/run1_attempt1_aborted/service_container.log
        results/run1_attempt1_aborted/service_info.json
        results/run1_attempt1_aborted/timings.tsv
script: scripts/run_reference_through_chap.sh
        sha256:4ec3791cc659e29aa42cf62790dfc1369fe6b53a734415ee9616fbb1ad53d8ff (version at fcd60ea)
        scripts/ewars_config.yaml
        sha256:db6143456deba36502ef455d8d468618408641e7222fe47e69b4cb30992dee94
invocation: bash analysis/01_referenceThroughChap/run.sh at commit fcd60ea (writing to results/run1, renamed
  to results/run1_attempt1_aborted before the next attempt)
inputs: ../../Archive/dev-data/monthly_ewars/historic_data.csv  sha256:ec9c37bd05009b85e01c336e743a53d392a984692e32a6f4103bf7dc79861e4b
        ../../Archive/dev-data/weekly_nicaragua/nicaragua_weekly_data_pre2018.csv  sha256:acc52a4effaab82ee8bfd0f465d48ac0642d6f3734ae0a2718b438cb71c4dca8
environment: node env/ (chap-core b8c8f788 from its uv.lock, Python 3.13; EWARS image sha256:959fb4f0…c6ff88, linux/amd64 under emulation on Docker 27.4.0, darwin arm64)
seeds: none settable (CH-10)
commit: fcd60ea
instructions-commit: 400536d
node: analysis/01_referenceThroughChap
produced: 2026-10-14
alternatives-considered: deleting the attempt. Kept: it is the record of CH-09 (the script stopped after the first
  failed evaluation) and the first observation of CH-07.
agency: agent-autonomous

## Since: the script changed
At fa74b72 PS4 lost its command substitution (CH-09); at 687755b the inputs were reduced to the data contract and
the weather provider made explicit. The current version, which produced run1, is
script: scripts/run_reference_through_chap.sh
        sha256:89babdc84cda3ad921a4fdb2076af7ff3adf88c134a54ade9618e7a6f6bec669
Nothing has run on the attempt-1 version since.
