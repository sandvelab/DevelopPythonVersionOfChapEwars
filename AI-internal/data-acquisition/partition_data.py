"""Partition the project's data into development and sealed holdout sets.

Reads only from Archive/<repo>/src (pinned clones) and writes:
  Archive/dev-data/    the only data development ever sees
  Archive/holdout/     sealed until phase E; not opened, plotted or summarised before then
each with sha256sums.txt. Rows are copied byte-for-byte (no parsing into floats), so the
files are exact subsets of the archived originals.

Selection (plan 26-10-14_pythonEwarsForChap, batch 1; decided on file names, columns, row
counts, location ids and period ranges only):
  dev  monthly : chapkit_ewars_model example_data_monthly/{historic,future}_data.csv
  dev  weekly  : chap-core nicaragua_weekly_data.csv, rows with period start < WEEKLY_CUT
  dev  smoke   : chapkit_ewars_model example_data/{training,future}_data.csv (8 periods)
  hold monthly : chap-core laos_subset.csv (3 locations, no overlap with dev)
  hold weekly  : chap-core nicaragua_weekly_data.csv in full; evaluation targets are the
                 periods starting >= WEEKLY_CUT (the earlier rows are their history)
Usage: python3 AI-internal/data-acquisition/partition_data.py  (from the repository root)
"""
import csv, hashlib, io, pathlib, shutil, sys

WEEKLY_CUT = "2018-01-01"
ROOT = pathlib.Path(__file__).resolve().parents[2]
A = ROOT / "Archive"
E = A / "chapkit_ewars_model/src"
C = A / "chap-core/src/example_data"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_sums(d):
    lines = [f"{sha(p)}  {p.relative_to(d)}" for p in sorted(d.rglob("*.csv"))]
    (d / "sha256sums.txt").write_text("\n".join(lines) + "\n")


def filter_rows(src, dst, keep):
    text = src.read_text()
    lines = text.splitlines(keepends=True)
    header = next(csv.reader([lines[0]]))
    i = header.index("time_period")
    out = [lines[0]] + [ln for ln in lines[1:] if keep(next(csv.reader([ln]))[i])]
    dst.write_text("".join(out))
    return len(out) - 1


def main():
    dev, hold = A / "dev-data", A / "holdout"
    for d in (dev, hold):
        if d.exists():
            sys.exit(f"{d} exists; refusing to overwrite a sealed partition")
    (dev / "monthly_ewars").mkdir(parents=True)
    (dev / "weekly_nicaragua").mkdir()
    (dev / "smoke_ewars_example_data").mkdir()
    (hold / "monthly_laos").mkdir(parents=True)
    (hold / "weekly_nicaragua").mkdir()
    for f in ("historic_data.csv", "future_data.csv"):
        shutil.copy2(E / "example_data_monthly" / f, dev / "monthly_ewars" / f)
    for f in ("training_data.csv", "future_data.csv"):
        shutil.copy2(E / "example_data" / f, dev / "smoke_ewars_example_data" / f)
    n = filter_rows(C / "nicaragua_weekly_data.csv",
                    dev / "weekly_nicaragua/nicaragua_weekly_data_pre2018.csv",
                    lambda tp: tp.split("/")[0] < WEEKLY_CUT)
    shutil.copy2(C / "laos_subset.csv", hold / "monthly_laos/laos_subset.csv")
    shutil.copy2(C / "nicaragua_weekly_data.csv", hold / "weekly_nicaragua/nicaragua_weekly_data.csv")
    write_sums(dev)
    write_sums(hold)
    print(f"weekly dev rows kept: {n}")
    for d in (dev, hold):
        for p in sorted(d.rglob("*.csv")):
            rows = sum(1 for _ in p.open()) - 1
            print(f"{p.relative_to(A)}\trows={rows}")


if __name__ == "__main__":
    main()
