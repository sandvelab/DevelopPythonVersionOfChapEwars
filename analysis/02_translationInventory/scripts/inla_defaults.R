# Run inside the R reference image. Writes, as one table, every INLA setting the EWARS fit
# depends on: the hyperparameter defaults of the three model components it uses, the control
# defaults it does not override, the values it does set, and the defaults of the posterior
# sampler. Values are read from the installed INLA (inla.models(), the control defaults,
# getOption, formals), not from documentation.
#
# Usage (in the image): Rscript inla_defaults.R <out_tsv>
out <- commandArgs(trailingOnly = TRUE)[1]
suppressPackageStartupMessages(library(INLA))
ns <- asNamespace("INLA")
rows <- list()
add <- function(group, setting, value, source)
  rows[[length(rows) + 1]] <<- data.frame(group = group, setting = setting,
                                          value = paste(deparse(value), collapse = " "),
                                          source = source, stringsAsFactors = FALSE)
m <- inla.models()
for (comp in list(c("likelihood", "nbinomial"), c("latent", "iid"), c("latent", "rw1"))) {
  def <- m[[comp[1]]][[comp[2]]]
  for (h in names(def$hyper)) {
    hh <- def$hyper[[h]]
    g <- paste0(comp[2], " ", h, " (", as.vector(hh$name), ")")
    src <- sprintf("inla.models()$%s$%s$hyper$%s", comp[1], comp[2], h)
    add(g, "prior", as.vector(hh$prior), src)
    add(g, "prior parameters", as.vector(hh$param), src)
    add(g, "initial (internal scale)", as.vector(hh$initial), src)
    add(g, "fixed", as.vector(hh$fixed), src)
    add(g, "to.theta (user -> internal)", body(hh$to.theta), src)
  }
  if (!is.null(def$constr)) add(comp[2], "constr (sum-to-zero by default)", def$constr,
                                sprintf("inla.models()$%s$%s$constr", comp[1], comp[2]))
}
add("rw1", "min.diff", m$latent$rw1$min.diff, "inla.models()$latent$rw1$min.diff")

ci <- get("inla.set.control.inla.default", envir = ns)()
for (s in c("strategy", "int.strategy", "fast", "h", "dz", "diff.logdens", "npoints",
            "adaptive.max", "improved.simplified.laplace"))
  add("control.inla default", s, ci[[s]], "inla.set.control.inla.default()")
add("control.inla default", "control.vb$enable", ci$control.vb$enable, "inla.set.control.inla.default()$control.vb")
add("control.inla default", "control.vb$strategy", ci$control.vb$strategy, "inla.set.control.inla.default()$control.vb")
cf <- get("inla.set.control.fixed.default", envir = ns)()
for (s in c("mean", "mean.intercept", "prec", "prec.intercept"))
  add("control.fixed default", s, cf[[s]], "inla.set.control.fixed.default()")
add("inla() default", "inla.mode", inla.getOption("inla.mode"), "inla.getOption('inla.mode')")
add("inla() default", "num.threads", inla.getOption("num.threads"), "inla.getOption('num.threads')")

# What predict.R sets explicitly (copied from the archived predict.R:192-197, for the join).
add("set by predict.R", "family", "nbinomial", "predict.R:192")
add("set by predict.R", "offset", quote(log(E)), "predict.R:192")
add("set by predict.R", "control.inla$strategy", "adaptive", "predict.R:193")
add("set by predict.R", "control.compute", quote(list(dic = TRUE, config = TRUE, cpo = TRUE, return.marginals = FALSE)), "predict.R:194")
add("set by predict.R", "control.fixed", quote(list(correlation.matrix = TRUE, prec.intercept = 1e-04, prec = precision)), "predict.R:195")
add("set by predict.R", "control.predictor", quote(list(link = 1, compute = TRUE)), "predict.R:196")

fs <- formals(get("inla.posterior.sample", envir = ns))
for (s in c("intern", "use.improved.mean", "skew.corr", "seed"))
  add("inla.posterior.sample default", s, fs[[s]], "formals(inla.posterior.sample)")

tab <- do.call(rbind, rows)
write.table(tab, out, sep = "\t", quote = FALSE, row.names = FALSE)
cat(nrow(tab), "settings written\n")
