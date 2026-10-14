# Data acquisition

Scripts that bring external repositories and data into `Archive/`, with their logs.

- `fetch_repos.sh` (+ `.log`) — clones the four anchor repositories, pinned by commit.
- `partition_data.py` (+ `.log`) — builds `Archive/dev-data/` and the sealed `Archive/holdout/`.
