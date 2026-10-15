# Run inside the R reference image. Runs the archived predict.R's own predict_chap() on one
# historic/future pair and one config, with taps that write what the model computes at each
# fidelity layer (plan §2), and with the posterior sampler seeded.
#
# The archived code is not copied out or edited. predict.R is parsed and every top-level
# expression is evaluated as it stands, except the final CLI block
# (`if (!interactive()) predict_chap(...)`), which is checked to be exactly that. The
# instrumented function is then built from predict_chap's own parsed body: statements are
# located by their exact text, tap calls are inserted between them, and exactly one
# statement is replaced — the sampler call gains `seed =`, preceded by set.seed() (JC-15).
# The resulting body is written to the run directory beside a list of the changes.
# dlnm::crossbasis is wrapped (a global shadowing the package's) so that the basis
# attributes — knots, boundary knots, lag df — are recorded; the call itself is unchanged.
#
# Usage (in the image):
#   Rscript instrument_reference.R <ewars_scripts_dir> <historic.csv> <future.csv>
#           <config.yml> <out_dir> <r_seed> <inla_seed>
#
# Writes to <out_dir>:
#   L1/L2  model_frame.csv.gz     the data frame passed to inla() (derived columns + basis)
#          formula.txt          the formula passed to inla()
#          crossbasis.json      attributes of each crossbasis() result
#   L3     fixed.csv, hyperpar.csv, random_<term>.csv, linear_predictor.csv.gz,
#          fitted_values.csv.gz INLA's posterior summaries
#          configs.csv          the hyperparameter integration points, with log posterior
#          fit_info.json        version, engine settings as resolved, nconfig, timings, threads
#   L4     posterior_draws.csv.gz   theta[1] and Predictor[idx.pred] per sample (xx.s)
#          hyperpar_draws.csv       the hyperparameters of every posterior sample
#          predictions.csv          predict.R's own output (time_period, location, sample_0..999); gzipped by run_fits.sh
#          offset_check.csv.gz      CH-19: Predictor - (reconstructed linear predictor) vs log(E)
#   instrumented_predict_chap.R, instrumentation.txt

opt <- commandArgs(trailingOnly = TRUE)
stopifnot(length(opt) == 7)
src_dir <- normalizePath(opt[1])
in_hist <- normalizePath(opt[2])
in_fut <- normalizePath(opt[3])
in_cfg <- normalizePath(opt[4])
out_dir <- opt[5]
.r_seed <- as.integer(opt[6])
.inla_seed <- as.integer(opt[7])
stopifnot(!is.na(.r_seed), !is.na(.inla_seed), .inla_seed > 0L)
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
out_dir <- normalizePath(out_dir)
t_start <- proc.time()[["elapsed"]]

# A writable copy of the archived scripts: predict.R sources scripts/lib.R relative to the
# working directory and saves model.rds into it (discarded here: an R-specific binary).
wd <- tempfile("ewars")
dir.create(file.path(wd, "scripts"), recursive = TRUE)
stopifnot(all(file.copy(file.path(src_dir, c("predict.R", "lib.R")), file.path(wd, "scripts"))))
setwd(wd)

# --- 1. predict.R, evaluated verbatim up to its CLI block --------------------------------
exprs <- parse("scripts/predict.R", keep.source = FALSE)
cli <- exprs[[length(exprs)]]
stopifnot(identical(cli[[1]], as.name("if")),
          identical(paste(deparse(cli[[2]]), collapse = ""), "!interactive()"))
for (e in exprs[-length(exprs)]) eval(e, globalenv())

.cb_record <- list()
crossbasis <- function(x, ...) {
  b <- dlnm::crossbasis(x, ...)
  a <- attributes(b)
  .cb_record[[length(.cb_record) + 1]] <<- a[setdiff(names(a), c("dim", "dimnames"))]
  b
}

# --- 2. Taps -----------------------------------------------------------------------------
num17 <- function(d) {  # doubles at 17 significant digits: round-trips exactly
  d[] <- lapply(d, function(x) if (is.double(x)) ifelse(is.na(x), NA, sprintf("%.17g", x)) else x)
  d
}
wcsv <- function(d, f) {  # a name ending .gz is written gzip-compressed
  if (endsWith(f, ".gz")) { con <- gzfile(file.path(out_dir, f), "w"); on.exit(close(con)) } else con <- file.path(out_dir, f)
  write.csv(num17(d), con, row.names = FALSE)
}
summ <- function(s) data.frame(name = rownames(s), s, check.names = FALSE, row.names = NULL)

.tap_frame <- function(df, formula) {
  wcsv(df, "model_frame.csv.gz")
  writeLines(paste(trimws(deparse(formula, width.cutoff = 500L)), collapse = " "), file.path(out_dir, "formula.txt"))
  jsonlite::write_json(.cb_record, file.path(out_dir, "crossbasis.json"), auto_unbox = TRUE,
                       digits = NA, pretty = TRUE, null = "null", na = "null")
}

.t_fit <- NA_real_
.tap_fit <- function(model, elapsed) {
  .t_fit <<- elapsed
  wcsv(summ(model$summary.fixed), "fixed.csv")
  wcsv(summ(model$summary.hyperpar), "hyperpar.csv")
  for (term in names(model$summary.random))
    wcsv(model$summary.random[[term]], paste0("random_", term, ".csv"))
  wcsv(summ(model$summary.linear.predictor), "linear_predictor.csv.gz")
  wcsv(summ(model$summary.fitted.values), "fitted_values.csv.gz")
  cs <- model$misc$configs
  cfg <- do.call(rbind, lapply(cs$config, function(k)
    data.frame(t(setNames(k$theta, paste0("theta_", seq_along(k$theta)))),
               log_posterior = k$log.posterior, log_posterior_orig = if (is.null(k$log.posterior.orig)) NA else k$log.posterior.orig)))
  wcsv(cfg, "configs.csv")
  ca <- model$.args$control.inla
  info <- list(
    inla_version = as.character(packageVersion("INLA")),
    dlnm_version = as.character(packageVersion("dlnm")),
    r_version = R.version.string,
    inla_mode = model$.args$inla.mode,
    strategy = ca$strategy, int_strategy = ca$int.strategy,
    vb_enable = ca$control.vb$enable,
    num_threads_option = inla.getOption("num.threads"),
    num_threads_fit = model$.args$num.threads,
    nconfig = cs$nconfig,
    theta_tags = model$misc$theta.tags,
    theta_mode = unname(model$mode$theta),
    mode_status = model$mode$mode.status,
    dic = model$dic$dic,
    cpu_used = as.list(model$cpu.used),
    fit_elapsed_seconds = elapsed,
    n_rows = nrow(model$.args$data),
    r_seed = .r_seed, inla_seed = .inla_seed
  )
  jsonlite::write_json(info, file.path(out_dir, "fit_info.json"), auto_unbox = TRUE, digits = NA,
                       pretty = TRUE, null = "null", na = "null")
}

.tap_samples <- function(xx, xx.s, df, idx.pred, model) {
  rownames(xx.s) <- c("theta1", paste0("Predictor:", idx.pred))
  colnames(xx.s) <- paste0("draw_", seq_len(ncol(xx.s)))
  wcsv(data.frame(row = rownames(xx.s), xx.s, check.names = FALSE), "posterior_draws.csv.gz")
  hp <- do.call(rbind, lapply(xx, function(z) z$hyperpar))
  wcsv(as.data.frame(hp, check.names = FALSE), "hyperpar_draws.csv")

  # CH-19: does Predictor include the log(E) offset? Rebuild the linear predictor of every
  # row from the first draw's latent components and compare. Indexing follows INLA's f():
  # values = sorted unique covariate values; replicate r puts value j at (r-1)*n + j.
  lat <- xx[[1]]$latent[, 1]
  comp <- function(tag) lat[startsWith(names(lat), paste0(tag, ":"))]
  vals <- function(v) sort(unique(v))
  eta <- rep(comp("(Intercept)"), nrow(df))
  fixed <- setdiff(rownames(model$summary.fixed), "(Intercept)")
  for (b in fixed) { x <- df[[b]]; stopifnot(!is.null(x)); x[is.na(x)] <- 0; eta <- eta + comp(b) * x }
  u_sp <- vals(df$ID_spat)
  eta <- eta + comp("ID_spat")[(df$ID_year - 1) * length(u_sp) + match(df$ID_spat, u_sp)]
  u_cy <- vals(df$ID_time_cyclic)
  eta <- eta + comp("ID_time_cyclic")[match(df$ID_time_cyclic, u_cy)]
  if ("ID_time_cyclic2" %in% names(model$summary.random)) {
    u_cy2 <- vals(df$ID_time_cyclic2)
    eta <- eta + comp("ID_time_cyclic2")[(df$ID_spat - 1) * length(u_cy2) + match(df$ID_time_cyclic2, u_cy2)]
  }
  pred <- comp("Predictor")
  stopifnot(length(pred) == nrow(df))
  wcsv(data.frame(row = seq_len(nrow(df)), Predictor = pred, eta_rebuilt = eta, log_E = log(df$E),
                  residual = pred - eta - log(df$E)), "offset_check.csv.gz")
}

# --- 3. The instrumented predict_chap -----------------------------------------------------
stmts <- as.list(body(predict_chap))[-1]
txt <- vapply(stmts, function(s) paste(deparse(s, width.cutoff = 500L), collapse = "\n"), "")
at <- function(prefix) {
  i <- which(startsWith(txt, prefix))
  if (length(i) != 1L) stop("statement not found exactly once: ", prefix)
  i
}
i_spat <- at("df$ID_spat <- as.integer(as.factor(df$ID_spat))")
i_inla <- at("model <- inla(formula = lagged_formula")
i_samp <- at("xx <- inla.posterior.sample(s, model)")
i_eval <- at("xx.s <- inla.posterior.sample.eval(")
stopifnot(txt[i_samp] == "xx <- inla.posterior.sample(s, model)",
          i_spat < i_inla, i_inla < i_samp, i_samp < i_eval)

after <- list()
after[[as.character(i_spat)]] <- list(quote(.tap_frame(df, lagged_formula)))
after[[as.character(i_inla)]] <- list(quote(.tap_fit(model, proc.time()[["elapsed"]] - .t0)))
after[[as.character(i_eval)]] <- list(quote(.tap_samples(xx, xx.s, df, idx.pred, model)))
before <- list()
before[[as.character(i_inla)]] <- list(quote(.t0 <- proc.time()[["elapsed"]]))
repl <- list()
repl[[as.character(i_samp)]] <- list(quote(set.seed(.r_seed)),
                                        quote(xx <- inla.posterior.sample(s, model, seed = .inla_seed)))
new <- list()
log_lines <- character()
for (i in seq_along(stmts)) {
  k <- as.character(i)
  for (q in before[[k]]) { new <- c(new, q); log_lines <- c(log_lines, sprintf("inserted before statement %d: %s", i, deparse(q))) }
  if (!is.null(repl[[k]])) {
    new <- c(new, repl[[k]])
    log_lines <- c(log_lines, sprintf("replaced statement %d [%s] by: %s", i, txt[i],
                                      paste(vapply(repl[[k]], function(q) deparse(q), ""), collapse = "; ")))
  } else new <- c(new, stmts[[i]])
  for (q in after[[k]]) { new <- c(new, q); log_lines <- c(log_lines, sprintf("inserted after statement %d: %s", i, deparse(q))) }
}
predict_chap_instrumented <- predict_chap
body(predict_chap_instrumented) <- as.call(c(as.name("{"), new))
writeLines(deparse(predict_chap_instrumented, width.cutoff = 500L), file.path(out_dir, "instrumented_predict_chap.R"))
writeLines(c(sprintf("predict_chap body: %d statements; instrumented: %d", length(stmts), length(new)), log_lines),
           file.path(out_dir, "instrumentation.txt"))

# --- 4. Run ------------------------------------------------------------------------------
predict_chap_instrumented(in_hist, in_fut, file.path(out_dir, "predictions.csv"), in_cfg)
info <- jsonlite::read_json(file.path(out_dir, "fit_info.json"))
info$total_elapsed_seconds <- proc.time()[["elapsed"]] - t_start
jsonlite::write_json(info, file.path(out_dir, "fit_info.json"), auto_unbox = TRUE, digits = NA,
                     pretty = TRUE, null = "null", na = "null")
cat("done:", out_dir, "\n")
