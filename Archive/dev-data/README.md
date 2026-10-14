# Development data

The only data development ever sees. Exact byte-for-byte copies or row subsets of files in
the pinned clones; never edited (data files cannot carry the IS_SHADOW marker — this README
states it instead). Checksums in `sha256sums.txt`; origin in `provenance.md`.

- `monthly_ewars/` — the EWARS repo's monthly example (23 locations, 2001-01..2017-06).
- `weekly_nicaragua/` — chap-core's Nicaragua weekly data, periods starting before 2018-01-01.
- `smoke_ewars_example_data/` — the EWARS repo's small `example_data/` (13 locations,
  8 periods): a smoke test only, too short for a backtest.
