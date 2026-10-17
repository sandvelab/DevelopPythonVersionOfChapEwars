# R-INLA 25.10.19: how the CHAP-EWARS nbinomial model is fitted and sampled (spec from the archived sources)

Path abbreviations (all under `Archive/`):

- `G/` = `r-inla-gmrflib/src/gmrflib/`
- `P/` = `r-sources/r-inla/src/inlaprog/src/`
- `R/` = `r-sources/r-inla/src/rinla/R/`
- `I/` = `r-sources/reference-image/`

Citations are `file:line` or `file:line-line`. "UNRESOLVED" means the archived sources do not settle the point.

## 0. Which code path runs

- `inla.mode="compact"` is the default. `R/inla.R:505-506` maps "experimental" to "compact", and the binary is called with `-Pcompact` (`R/inla.R:2138-2139`). The C driver is `inla_INLA_preopt_experimental` (`P/inla.c:5759`), which calls `GMRFLib_ai_INLA_experimental` (`P/inla.c:6407-6419`, defined at `G/approx-inference.c:1075`). That function asserts compact mode (`G/approx-inference.c:1131-1132`).
- The classic-mode code (`G/approx-inference--classic.c`, `P/inla-classic.c`) is **not** used.

## 1. Priors

### 1a. pc.mgamma(lambda = 7) on theta_1 = log(size)

The defaults are prior "pc.mgamma", param 7, initial log(10) = 2.302585, `to.theta = log`, `from.theta = exp` (`I/inla_models_selected.txt:1-11`). The name maps to `priorfunc_pc_mgamma` (`P/inla-priors.c:507-511`).

The prior is added to the log posterior as `PRIOR_EVAL(ds->data_prior, &log_size)`, with `log_size = theta[count]` (`P/inla.c:2208-2216`). So it is evaluated at theta = log(size) itself.

`priorfunc_pc_mgamma(x)` returns `priorfunc_pc_gamma(-x)` (`P/inla-priors.c:1689-1696`). `priorfunc_pc_gamma(x')` is at `P/inla-priors.c:1666-1687`, with a = exp(x') and a_inv = 1/a.

Substituting x' = -theta gives a = 1/s and a_inv = s, where s = size = e^theta:

```
d(s)        = sqrt( 2 * ( log(s) - digamma(s) ) )
SPECIAL(s)  = log( trigamma(s) - 1/s )                          if s <= 1e4
            = -2 log s - log 2 + 1/(3s) - 1/(18 s^2) - 22/(405 s^3)   if s > 1e4   (P/inla-priors.c:1671-1673)
log pi(theta) = log(lambda) - lambda*d(s) - 2*log(a) - log(d(s)) + SPECIAL(s) + x'
              = log(lambda) - lambda*d(s) + theta - log(d(s)) + log(trigamma(s) - 1/s)
```

The two forms agree because -2 log a + x' = 2 theta - theta = theta.

- **It is a proper density in theta.** It is the exponential PC density on the distance d, times |dd/da|, times the Jacobian a = e^{x'} that the `+ x[0]` term supplies (`P/inla-priors.c:1683`). The map x' = -theta has unit Jacobian.
- There is no factor 1/2.
- lambda = 7, taken from `parameters[0]`.

### 1b. loggamma(a = 1, b = 5e-5) on theta = log(precision), for both iid and rw1

The defaults are in `I/inla_models_selected.txt:14-34`. `priorfunc_loggamma(x)` = `priorfunc_gamma(exp(x)) + x` (`P/inla-priors.c:2091-2098`). `priorfunc_gamma` uses rate `parameters[1]`; for a == 1 it returns `-x/b' - log b'` with b' = 1/rate (`P/inla-priors.c:2171-2199`). So:

```
log pi(theta) = log(b) + theta - b*exp(theta),   b = 5e-5      (density in theta, Jacobian included)
```

In general: a log b - lgamma(a) + a theta - b e^theta.

The prior is evaluated at theta = log precision in `extra()` (`P/inla.c:2944-2946`).

### 1c. Fixed effects

- The intercept and every covariate are **latent nodes** ("linear" terms). In compact mode they are appended after all f() blocks (`P/inla.c:5799-5815`, and the BETA type in `G/pre-opt.c:886-895`).
- Prior: Gaussian with mean 0 and precision `prec.intercept` = 1e-4 for "(Intercept)", `prec` = 0.01 for the others (`R/sections.R:1706-1720`).
- In the prior precision this is a diagonal entry `prior_precision[k]` (`G/pre-opt.c:886-895`). The b-vector entry is prec*mean = 0 (`P/inla.c:5814-5816`).
- Their normalising constant `-0.5 log(2pi) + 0.5 log(prec) - 0.5 prec mean^2` is added in `extra()` (`P/inla.c:2879-2884`). It does not depend on theta.

## 2. nbinomial likelihood (variant 0)

The function is `loglikelihood_negative_binomial` (`P/inla-likelihood.c:4447-4621`), registered for "NBINOMIAL" at `P/inla-parse.c:1050-1052`.

- size = exp(theta_1) for variant 0 (`P/inla-likelihood.c:4467`).
- `x[i]` is the linear predictor **without** the offset. The offset `off = ds->offset[idx]` is added inside the likelihood (`P/inla.c:134,138,159`): eta_tot = x + off.
- With R's `offset=log(E)`, INLA's own E is 1 (UNRESOLVED from the C source alone, but implied because the call does not pass `E=`). Then mu = exp(x + off).

The log-likelihood, as optimised at `P/inla-likelihood.c:4553-4590`:

```
l(y | eta) = lgamma(y+s) - lgamma(s) - lgamma(y+1) + s*log(s) + y*log(E)
             - (s+y) * [ log(s) + log1p( (E/s) * exp(eta+off) ) ] + y*(eta+off)
           = lgamma(y+s) - lgamma(s) - lgamma(y+1) + s log(s/(s+mu)) + y log(mu/(s+mu)),   mu = E*exp(eta+off)
```

For small y, `lgamma(y+s) - lgamma(s)` is computed as `sum_{k<y} log(k+s)` (`P/inla-likelihood.c:4537-4545`). It is mathematically identical.

## 3. Latent model components

### 3a. Cyclic RW1 with scale.model = TRUE

- Structure matrix, cyclic order 1 (`G/rw.c:58-77`): Q_ii = 2*prec and Q_{i,i±1 mod n} = -prec, where prec = exp(theta) * prec_scale (`G/rw.c:44-48`). That is, Q = tau * s * R_cyc.
- The graph and model are built at `P/inla-parse.c:17966-18037`. Rank deficiency = 1 for cyclic order >= 1 (`P/inla-parse.c:18020-18026`).

The scale s is computed by `GMRFLib_rw_scale` (`G/rw.c:957-1081`):

1. Build R_cyc multiplied by `prec_scale_guess` = n - 1 (`G/rw.c:1012-1022`).
2. Add eps = sqrt(DBL_EPSILON) ~ 1.49e-8 to the diagonal (`G/rw.c:1031-1033`), multiplying it by 10 on failure.
3. Impose the sum-to-zero constraint (`G/rw.c:1015-1019`).
4. Compute the constrained marginal variances V_ii.
5. Set s = exp(mean_i log V_ii) * (n - 1) (`G/rw.c:1066-1072`).

So s is the geometric mean of the constrained marginal variances of R_cyc. The V_ii are computed under (n-1) R + eps I, and the factor n - 1 undoes that scaling. For a cyclic RW1 all V_ii are equal by symmetry.

`diagonal`: f() sets `diagonal = inla.set.f.default()$diagonal = 1e-4` whenever `constr=TRUE` and the user gave none (`R/f.R:861-867`, `R/set.default.arguments.R:229-230`).

- rw1 has constr = TRUE by default (`I/inla_models_selected.txt:31`), so **1e-4 is added to every diagonal entry of the rw1 prior precision**. This includes every replicate.
- It is added unscaled, as `value += a->f_diag[...]` (`G/pre-opt.c:856-859`).
- iid has constr = FALSE, so its diagonal is 0.
- `control.inla$diagonal` = 0 (`I/inla_control_defaults.txt:101-102`) is a separate "expert emergency" term and adds nothing (`P/inla.c:6104-6107`).

### 3b. replicate + constr

The replicated precision is block-diagonal (`Qfunc_replicate`). The constraint becomes **one sum-to-zero constraint per replicate**, built by `inla_make_constraint2` (`P/inla-parse.c:18697-18715`, `P/inla.c:915-960`). All constraints of all f-terms are stacked into one latent A_c x = 0 (`G/pre-opt.c:150-230`).

- The first rw1 has nrep = 1, so 1 constraint.
- The rw1 with `replicate=ID_spat` has n_spat constraints.
- The iid has none.

### 3c. Normalising constant in log pi(theta | y)

In `extra()` (`P/inla.c:2920-2948`), for iid and rw1:

```
val += nrep * [ -0.5 log(2pi) * (N - r) + 0.5 (N - r) * theta ] + log prior(theta)
```

Here N is the per-replicate size, r = f_rankdef, nrep = number of replicates; normc_g = 0 and gcorr = 1 without `group`.

- iid: r = 0 (N = n_spat, nrep = n_year).
- cyclic rw1: r = 1.
- The pseudo-determinant of R, the scale s, and the 1e-4 diagonal **do not appear**. They are constant in theta, except that the 1e-4 diagonal enters through the Gaussian approximation; see section 4.

## 4. Laplace approximation for pi(theta | y) in compact mode

**Latent field.** x = [f-term 1 (all replicates) | f-term 2 | ... | intercept | covariates]. Its dimension is N = sum of f_Ntotal + nlinear (`P/inla.c:5773-5779`, `G/approx-inference.c:1131`).

- The linear predictor is **not** part of x. It is eta = A_pred x (`GMRFLib_preopt_predictor`, `G/approx-inference.c:752-759`).
- Prior precision Q_0(theta) = blockdiag(tau_iid I per replicate, tau_rw s R_cyc + 1e-4 I per replicate, ..., diag(prec_beta)).
- The posterior precision of the Gaussian approximation (GA) is Q = Q_0 + A_pred' diag(c) A_pred (`G/pre-opt.c:996-1034`). c is updated by `GMRFLib_preopt_update` (`G/pre-opt.c:1433-1450`).

**GA / mode, Newton iteration.** This is `GMRFLib_init_GMRF_approximation_store__intern` (`G/approx-inference.c:637-1073`).

1. Expand each l_i around eta0 = A x_current, using a 5-point numerical stencil with step `step_len` = 1e-4 (`P/inla-parse.c:18956-18960`, `G/blockupdate.c:69-170,174-494`):
   ```
   a_i = l(eta0) - eta0 l'(eta0) + 0.5 eta0^2 l''(eta0)
   b_i = l'(eta0) - eta0 l''(eta0)
   c_i = -l''(eta0)
   ```
   `cmin = -Inf` (R default), so c is not truncated.
2. Solve Q mu = A_pred' b, then condition by kriging, Sigma_c-style (`G/problem-setup.c:887-905`):
   ```
   mu_c = mu - Q^{-1} A_c' (A_c Q^{-1} A_c' + 1.49e-8 I)^{-1} A_c mu
   ```
   The constraint covariance has 1.49e-8 = sqrt(DBL_EPSILON) added to its diagonal (`G/problem-setup.c:736-740`, `P/inla.c:7138`). R also writes `constr.marginal.diagonal` = 1.49e-8 (`I/inla_control_defaults.txt:177`).
3. Update x <- x + f (mu_c - x) (`G/approx-inference.c:884-898`). Here f = min(1, (iter+1) * nr_step_factor). R passes step.factor = -0.1, which means "0.1 on the very first call per thread, else 1" (`G/approx-inference.c:447-458`).
4. Stop when RMS(mu_c - x) < tolerance.step = 0.005/2000 = 2.5e-6 (`G/approx-inference.c:892,945`; `R/sections.R:1142-1145`). The cap is 25 iterations (`G/optimize.c:24`); on failure it restarts with a trust region.

The final GA is the one built at the last expansion point. Its constrained mean `mean_constr` is the "mode" (`G/approx-inference.c:504-506`).

**Objective.** `G/approx-inference.c:512-524` and `G/domin-interface.c:283-330`:

```
log pi~(theta|y) = extra(theta) + sum_i a_i - log p_G(x = 0 | theta, y, A_c x = 0)
```

extra(theta) holds all log priors from section 1 and the normalising constants from section 3c.

log p_G at x = 0 comes from `G/problem-setup.c:957-1033`:

```
log p_G(0) = -n/2 log(2pi) + 0.5 log|Q| - 0.5 mu' Q mu                  (mu = UNconstrained GA mean)
             - 0.5 log|A_c A_c'|                                        ([Ax|x])
             + nc/2 log(2pi) + 0.5 log|S| + 0.5 (A_c mu)' S^{-1} (A_c mu)  (minus log [Ax])
S = A_c Q^{-1} A_c' + 1.49e-8 I
```

- **Yes, there is a constraint correction term.** log p_G is the density of x given A_c x = 0, computed as [x][Ax|x]/[Ax].
- Equivalent form: evaluated at x = mu_c, the quadratic term and the exp_corr term cancel. The evaluation point x = 0 is exact because the GA log-ratio is constant in x for the quadratic expansion.
- A Python version may equivalently use sum_i l_i(eta*) + [log p(x*|theta) with the INLA normalisation] - log p_G(x*) at the mode. Doing exactly the x = 0 form above is the safest match.

## 5. Mode search over theta

The settings below come from `G/approx-inference.c:1310-1398`, `G/domin-interface.c:1235-1482`, and the R defaults in `R/sections.R:1122-1145,1290-1305`.

- **Optimizer.** GMRFLib's own BFGS: `gsl_multimin_fdfminimizer_vector_bfgs3`, a copy of GSL bfgs2 in `G/bfgs3.c` (`G/domin-interface.c:1303-1307`). It uses step_size 1.0 and line-search tol 0.1 (`G/approx-inference.c:111-116`). The objective is -log pi~(theta|y).
- **Starting values.** 2.302585 for log size and 4 for each log precision (`I/inla_models_selected.txt`).
- **Tolerances.** tolerance = 0.005 gives epsf = 0.002, epsg = 0.005, epsx = 0.001, epsstep = 2.5e-6 (`R/sections.R:1122-1145`, `P/inla-parse.c:18849-18853`).
- **"smart" strategy** (`G/approx-inference.c:1324-1370`):
  - Part I uses **forward** differences for the gradient, with all eps multiplied by 5.
  - Part II restarts once (restart = max(1, 0)) with **central** differences and the original eps.
- **Gradient step.** h = 0.005 (`P/inla-parse.c:19083-19084`, `G/domin-interface.c:455,521,603`).
- **Stopping rule** (`G/domin-interface.c:1333-1356,1454-1457`): after at least 2 iterations, stop at the first of these:
  - ||grad||_2 < epsg;
  - RMS change of the best theta < epsx;
  - |change of best f| < epsf;
  - GSL failure (ENOPROG);
  - 1000 iterations.

  After every iteration the minimiser is restarted from the best point found so far, and the result is that best point (`G/domin-interface.c:1428-1466`).
- **"use.directions" = TRUE** (`R/sections.R:1302-1305`). Finite-difference steps are taken along the columns of an orthonormal matrix A. A is built from the most recent BFGS steps by modified Gram-Schmidt (`G/domin-interface.c:1250-1289,1365-1386,1175-1231`). Gradient and Hessian are transformed back to theta coordinates.

**Hessian** (`G/domin-interface.c:652-1061`):

- Central differences of -log pi~ with step **h_H = sqrt(0.005) = 0.07071**. The parser sets the Hessian step to sqrt(|H|) with H = 0.005 (`P/inla-parse.c:19095`). The step is taken along the direction columns (`G/domin-interface.c:730,1175-1186`).
- Diagonal: (f(+h) - 2 f0 + f(-h)) / h^2 (`:890`).
- Off-diagonal: (f(+,+) - f(-,+) - f(+,-) + f(-,-)) / (4h^2) (`:994`).
- **"stupid search":** if any of the 2n+1 diagonal evaluations is better than f0, or the best f changes during the Hessian, the mode moves to the better point and the Hessian is recomputed with h *= 1.05^count (`:750,844-869,1004-1015`; `G/approx-inference.c:1463-1506`).
- After that comes `ensure_spd` (`:1022`) and the eigen-decomposition H = V Lambda V' (`G/approx-inference.c:1544-1550`).
- Negative eigenvalues trigger a fall back to a diagonal Hessian (`:1567-1638`).

**Reparametrisation** (`G/approx-inference.c:579-607`):

```
theta(z) = theta* + V diag(1/sqrt(lambda)) z
```

The GSL eigenvalue order is unsorted. This is harmless because the design is symmetric under axis permutation and sign flips (section 7).

## 6. Skewness-corrected standard deviations

This is `G/approx-inference.c:1726-1813`. For each k:

```
step = sqrt(2)
zz = +step e_k  ->  theta = theta(zz),  D+ = log pi~(theta*) - log pi~(theta(+sqrt2 e_k))
corr_pos[k] = sqrt( step^2 / (2 D+) ) = sqrt(1/D+)   (1.0 if D+ <= 0)
corr_neg[k] likewise with -sqrt(2) e_k
```

`hessian.correct.skewness.only` = TRUE (`I/inla_control_defaults.txt:189`, written at `R/sections.R:1320`). So both are divided by gmean = sqrt(corr_pos * corr_neg) (`G/approx-inference.c:1805-1808`):

```
corr_pos <- sqrt(corr_pos/corr_neg),   corr_neg <- sqrt(corr_neg/corr_pos)   (product = 1)
```

Use: z_i = f * design_i * (design_i > 0 ? corr_pos[i] : corr_neg[i]) (`G/approx-inference.c:2017-2021`).

## 7. CCD design ("auto", 3 or 4 hyperparameters)

- R writes `int.strategy = auto`. The parser keeps AUTO (`P/inla-parse.c:19009-19012`). In the experimental routine AUTO becomes GRID (`G/approx-inference.c:1149-1151`).
- `GMRFLib_design_grid` with nhyper not equal to 1 or 2 returns `GMRFLib_design_ccd` (`G/design.c:31-37`). The point table is `G/designP.h` (nexp[3] = 15, nexp[4] = 25).
- Points for 3 hyperparameters: centre (0,0,0), the 6 axial points ±e_k, and the **full** 2^3 factorial (±1,±1,±1).
- Points for 4 hyperparameters: centre, the 8 axial points, and the full 2^4 = 16 factorial.
- Each non-centre point is scaled to unit norm (`G/design.c:226-235`). Axial points are therefore ±1 and factorial points are ±1/sqrt(m) per coordinate. int_weight = NaN.
- The radius uses f0 = 1.1 (`G/approx-inference.c:65`) and f = max(f0, 1) sqrt(m) (`G/approx-inference.c:1913-1919`). So every non-centre point sits at |z| = f before the skewness factors:
  - m = 3: f = 1.905256
  - m = 4: f = 2.2

**Weights**, applied because int_weight is NaN (`G/approx-inference.c:1913-1919,2063-2087`). N = number of points:

```
w      = 1 / ( (N-1) * (1 + exp(-f^2/2) * (f^2/m - 1)) )
w_orig = 1 - (N-1) w
m=3: w = 0.0690668, w_origo = 0.0330653   (log -2.672682, -3.409272)
m=4: w = 0.0409029, w_origo = 0.0183312   (log -3.196555, -3.999149)
```

Because N - 1 is used, the 6 axial and 8 factorial points get equal weights. The weights are **not** multiplied by the corr factors or by |det| terms.

- **log_posterior** = log pi~(theta_k|y) + log(w or w_origo) (`G/approx-inference.c:2071-2077`).
- **log_posterior_orig** = log pi~(theta_k|y) without the weight (`G/approx-inference.c:6455-6456`).
- R subtracts **max_k(log_posterior_orig)** from both (`R/collect.results.R:691-695`). So the centre has log.posterior_orig ~ 0 and log.posterior ~ log(w_origo).
- Configs whose log pi~ falls more than about 6.9 below the mode (prob < 1 - 0.999) are **not stored** (`G/approx-inference.c:2091-2094`, `G/globals.c:129`). This does not happen for typical CCD points.

## 8. strategy = 'adaptive'

- In compact mode `inla_INLA_preopt_experimental` sets `strategy = GAUSSIAN` unconditionally (`P/inla.c:6169`). It overrides whatever was parsed (`P/inla-parse.c:18908-18934`).
- The experimental routine only builds Gaussian latent marginals N(mode, sd) (`G/approx-inference.c:2124-2130`) and then applies the VB correction.
- **'adaptive' therefore has no effect in this version and mode.** It does not affect the configs, theta points, means or Q, so it does not affect `inla.posterior.sample`.

## 9. VB correction

**Enabling.**

- `control.vb$enable = "auto"` becomes TRUE in compact mode (`R/sections.R:1266-1269`).
- The strategy is written with `match.arg(c("mean","variance"), choices, several.ok=FALSE)` (`R/sections.R:1272-1274`). By R base semantics, `match.arg` returns the first element when arg is identical to choices. R base is not archived, so this rests on that semantics: the strategy is **"mean"**.
- The C side parses MEAN (`P/inla-parse.c:19272-19279`), so **only the mean is corrected**. There is no variance correction (`G/approx-inference.c:2140-2147`), `c_corrected` = 0, and the stored Q equals the GA precision.
- Settings: iter.max = 25, emergency = 25, f.enable.limit = (30, 25, 1024, 768) (`I/inla_control_defaults.txt:137-160`).

**Correction set S** (`P/inla.c:5842-5940`):

- All linear terms (intercept and covariates) are always in S.
- For each f-term: lim = max(0, min(30, floor(1024 / (nf * ngroup * nrep)))), where nf is the number of f-terms.
  - If n <= lim (n = per-replicate size), all nodes of all replicates are in S.
  - Otherwise lim nodes per replicate are taken at indices (j*len + k) mod n, j = 0..lim-1, with len = max(1, floor(n/lim)) and k = max(1, floor(len/2)).
  - If lim = 0, none are taken. Example: rw1-by-spat with n_spat > 341 when nf = 3.

**Algorithm**, per CCD config, after its GA (`GMRFLib_ai_vb_correct_mean_preopt`, `G/approx-inference.c:5168-5686`):

1. Start from m = GA mode (mean_constr) (`:5266-5272`). Let sd_i = sqrt(constrained Var_GA(x_i)).
2. M = Sigma_c[:, S], the constrained GA covariance columns. `GMRFLib_Qsolve(s)` applies the kriging correction (`G/problem-setup.c:321-388`; `:5307-5338`).
3. Predictor variances v_i = Var_GA(eta_i) are computed once and kept fixed (`:5371`).
4. Each iteration:
   - eta_i mean = (A_pred m)_i.
   - Using 15-point Gauss-Hermite quadrature with the N(0,1) kernel (`G/GMRFLibP.h:860`, `:5002-5075`):
     ```
     BB_i = -E[l_i'(eta)],  CC_i = -E[l_i''(eta)],   eta ~ N(eta_i mean, v_i)
     ```
   - Gradient of the KL objective: g = Q_0 (m - prior_mean) + A_pred' BB (`:5440-5450`).
   - MM = M' Q_GA M (`:5452-5480`). Q_GA is **tabulated once before the loop with force = 1** (`:5292`, `G/tabulate-Qfunc.c:81-97`), so MM ~ Sigma_c[S,S] is fixed, and **CC is effectively unused**.
   - delta = -pinv(MM) M' g. The pseudo-inverse drops eigenvalues below cbrt(eps) * max (`:5482-5503`; `G/lapack-interface.c:929`).
   - dm = M delta, with each component capped at ±5.001 sd_i (`:5203,5536-5546`).
   - m += dm.
   - Stop when max|dm_i/sd_i| < 0.01 or at iteration 25 (`:5622-5624`).
5. Abort and keep the mode if max|m - mode|/sd >= 25, delta is NaN, or the iteration diverges (dm increases 3 times in a row) (`:5550-5612`).
6. On success, `user_mean` = m for **all** latent nodes (`:5657-5665`). This becomes `cfg->improved_mean` (`G/approx-inference.c:2149-2151,6463`).

The objective is a quasi-Newton minimisation, in span(M), of 0.5 (m-mu0)'Q_0(m-mu0) - sum_i E_q[l_i], with fixed variances and the fixed Hessian Q_GA.

**Use in sampling.** `inla.posterior.sample(use.improved.mean=TRUE)` uses `improved.mean`, the VB-corrected mean, as mu (`I/installed_functions/INLA__inla.posterior.sample.R:121-123,139-141`).

## 10. inla.posterior.sample in compact mode

Source: `I/installed_functions/INLA__inla.posterior.sample.R`.

- **Preopt branch (lines 10-61).** It samples the latent x through a recursive call. It then forms Predictor = A x + offsets, with A = `configs$A` (npred x N) and offsets = `configs$offsets`. The offsets come from `R/collect.results.R:550`, which is the R `offset=log(E)`. It returns c(Predictor, latent).
- **Choice of config (lines 95-100).**
  ```
  p_k ∝ exp(log.posterior_k)      (log.posterior_k = log pi~(theta_k|y) + log w_k, relative)
  ```
  So the integration weights **are** included. Draws use `sample(1:nconfig, n, prob = p, replace = TRUE)`, sorted.
- **Latent draw (lines 121-125 / 139-143).**
  - Calls `inla.qsample(n_k, Q = cfg$Q, mu = cfg$improved.mean, constr = cs$constr)`. Q is the GA posterior precision for theta_k: Q_0 + A' diag(c) A + c_corrected(= 0) (`G/approx-inference.c:6416-6430`).
  - In C (`P/inla-modes.c:163-…`, `G/problem-setup.c:861-946`): x = mu + L^{-T} z, then x <- x - Q^{-1}A_c'(A_c Q^{-1} A_c' + 1.49e-8 I)^{-1}(A_c x - e), with e = 0.
  - The draw is therefore centred at the **kriged** improved mean. The VB mean is already nearly constrained, because dm lies in span(Sigma_c).
- **skew.corr = TRUE does nothing here.** In preopt mode the configs carry `skewness = rep(NA, n)` (`R/collect.results.R:657`). The sampler sets NA to 0 (line 229), so `zero.not` is empty and sample.corr = xx$sample (lines 239-244).
- **Theta in the samples (lines 152-160).**
  - `hyperpar` = from.theta(cfg$theta) = **exp(theta_k)**: size, prec_iid, prec_rw1.
  - These are the config's exact CCD theta values, so there are only 15 or 25 distinct values.
  - In `inla.posterior.sample.eval`, `theta` = `a.sample$hyperpar` (`I/installed_functions/INLA__inla.posterior.sample.eval.R:22-23`). So `theta[1]` is **size on the natural scale**, not log size.
  - The order is the data hyperparameter first, then the f-terms in formula order (`P/inla.c:2208-2216,2920-2946`).

## Five details most likely to matter numerically for matching INLA's predictive distribution

1. **Configs are drawn with p_k ∝ w_k * pi~(theta_k|y), and theta is reported only at the CCD points.**
   - w_origo is smaller than w: 0.033 vs 0.069 for m = 3, and 0.018 vs 0.041 for m = 4.
   - The points sit at radius f*corr. f = 1.905 for m = 3 and 2.2 for m = 4, with the skewness-only correction (corr_pos * corr_neg = 1).
   - `theta[1]` is exp(theta_1) = size.
2. **The latent mean is the VB-corrected mean, not the GA mode.** It is a "mean" strategy only, with Q_GA as the fixed Hessian, fixed predictor variances, 15-point GHQ, and the S-node selection rule. Covariance = the GA covariance, and constraints are applied by kriging. **skew.corr has no effect.**
3. **The Laplace objective.** It includes the constraint correction terms (+0.5 log|A_c Q^{-1} A_c'| - 0.5 log|A_c A_c'| + nc/2 log 2pi, with 1.49e-8 added). The prior normalisation is only nrep (N - r)/2 theta per term, while Q_0 has the **extra 1e-4 on the rw1 diagonal**, and **per-replicate sum-to-zero constraints**.
4. **The pc.mgamma prior** written as a density in theta = log size: log 7 - 7 d(s) + theta - log d(s) + log(psi'(s) - 1/s). Add **loggamma(1, 5e-5) with the +theta Jacobian** for the precisions, and **rw1 scaling s = geometric mean of the constrained variances of R_cyc**.
5. **The theta-mode and Hessian numerics, which set the CCD geometry.**
   - BFGS tolerances: epsg 0.005, epsf 0.002, epsx 0.001, after a 5x-looser forward-difference phase.
   - Central-difference Hessian with **h = sqrt(0.005) ≈ 0.0707** along the BFGS direction basis, with the "stupid search" re-centring.
   - Skewness factors from f(±sqrt2) in the eigen z-scale.
   - The rw1 axis is very skewed (+0.34 / -1.86 in the user's example), so the positions of its axial and factorial points depend sensitively on these.

UNRESOLVED or caveats:

- That INLA's internal E is 1 when R uses `offset=` is inferred, not read from source.
- `match.arg` semantics (VB strategy = "mean") rely on base R, which is not archived.
- The exact BFGS line search path and the direction matrix used for the Hessian are path-dependent. They are reproducible only by porting `G/bfgs3.c` and `G/domin-interface.c` verbatim. Their effect is O(h^2)/tolerance-level.
