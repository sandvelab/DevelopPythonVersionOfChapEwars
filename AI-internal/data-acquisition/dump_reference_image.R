# Run inside the R reference image (fetch_r_sources.sh mounts the output directory at /out).
# Records what the reference actually runs: package versions, the INLA model definitions and
# control defaults of the installed INLA, and the installed R code of the functions the EWARS
# model relies on, deparsed from the packages as installed (not from any source tree).
out <- "/out"
dir.create(file.path(out, "installed_functions"), showWarnings = FALSE, recursive = TRUE)

# The libraries predict.R and train.R load, in their order.
suppressPackageStartupMessages({
  library(yaml); library(jsonlite); library(INLA); library(dlnm); library(dplyr)
  library(sf); library(spdep)
})

pkgs <- c("INLA", "dlnm", "splines", "dplyr", "yaml", "jsonlite", "sf", "spdep", "Matrix", "stats")
writeLines(c("package\tversion",
             sprintf("%s\t%s", pkgs, vapply(pkgs, function(p) as.character(packageVersion(p)), ""))),
           file.path(out, "package_versions.tsv"))
writeLines(capture.output(sessionInfo()), file.path(out, "sessionInfo.txt"))
file.copy(system.file("DESCRIPTION", package = "INLA"), file.path(out, "INLA_DESCRIPTION"), overwrite = TRUE)
file.copy(system.file("DESCRIPTION", package = "dlnm"), file.path(out, "dlnm_DESCRIPTION"), overwrite = TRUE)

# INLA's model definitions for the three components the formula uses: defaults of every
# hyperparameter (prior, prior parameters, initial value, fixed or not, and the to.theta /
# from.theta maps between the user scale and INLA's internal scale).
m <- inla.models()
sink(file.path(out, "inla_models_selected.txt"))
for (nm in c("likelihood$nbinomial", "latent$iid", "latent$rw1")) {
  parts <- strsplit(nm, "\\$")[[1]]
  cat("################ inla.models()$", nm, "\n", sep = "")
  dput(m[[parts[1]]][[parts[2]]])
  cat("\n")
}
cat("################ inla.models()$prior (names)\n"); print(names(m$prior))
cat("################ inla.models()$prior$loggamma\n"); dput(m$prior$loggamma)
sink()

# Defaults of the control arguments predict.R passes or leaves at default.
sink(file.path(out, "inla_control_defaults.txt"))
for (f in c("inla.set.control.inla.default", "inla.set.control.fixed.default",
            "inla.set.control.predictor.default", "inla.set.control.compute.default",
            "inla.set.control.family.default")) {
  cat("################", f, "()\n")
  print(tryCatch(get(f, envir = asNamespace("INLA"))(), error = function(e) conditionMessage(e)))
  cat("\n")
}
sink()

# Installed R code of the functions the model calls or depends on.
dump_fun <- function(pkg, fn) {
  f <- get(fn, envir = asNamespace(pkg))
  writeLines(c(sprintf("# %s::%s, as installed (%s %s), deparsed", pkg, fn, pkg, packageVersion(pkg)),
               deparse(f)),
             file.path(out, "installed_functions", sprintf("%s__%s.R", pkg, fn)))
}
for (fn in c("inla.scale.model", "inla.posterior.sample", "inla.posterior.sample.eval",
             "inla.rw1", "inla.rw"))
  if (exists(fn, envir = asNamespace("INLA"))) dump_fun("INLA", fn)
for (fn in ls(asNamespace("dlnm"))) dump_fun("dlnm", fn)
for (fn in c("ns", "splineDesign", "bs")) dump_fun("splines", fn)
for (fn in c("rnbinom", "dnbinom")) dump_fun("stats", fn)
cat("done\n")
