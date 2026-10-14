# Claim

Which R calls does the EWARS model make, under the exact package versions in the reference image, what do INLA's defaults make of the ones left unspecified, and which have a trustworthy Python counterpart versus a gap that needs a parallel port or an inference candidate?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`) for `build_inventory.py`;
override: `env/` — the two R scripts run inside the R reference image, because they must read
the package versions the reference actually runs (`env/README.md`).

## Answers

1. **The model makes 171 calls to 65 distinct functions and formula terms; every one is
   mapped to Python** (`results/translation_inventory.md`, `results/unmapped.txt` empty).
   - 36 have a direct Python equivalent (data handling).
   - 13 are the model's own functions, ported line by line.
   - 8 are not needed in a Python service.
   - 3 have a Python counterpart that must be verified against R first: `crossbasis` and
     `equalknots` via dlnmpy, and `rnbinom`.
   - 3 are gaps needing a parallel port: the iid-with-replicate term and the two scaled
     cyclic RW1 terms.
   - 2 are the inference engine itself: `inla` and `inla.posterior.sample`
   (`results/coverage.tsv`).
2. **The installed INLA's defaults define much of the model**
   (`results/inla_defaults.tsv`):
   - the negative-binomial size has a `pc.mgamma` prior with λ = 7 on log size;
   - both precisions have `loggamma(1, 5e-05)` priors;
   - RW1 carries a sum-to-zero constraint;
   - the fit runs in `compact` mode, with `int.strategy` `auto` and the VB mean correction
     on;
   - posterior samples use improved means and a skewness correction.
3. **`sf`, `spdep` and `jsonlite` are loaded but never called**; `yaml` and `dplyr` are
   (`results/r_calls.tsv`).
