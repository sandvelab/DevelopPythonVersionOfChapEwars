# Diagnostic, not the reference as it runs: instrument_reference.R with INLA's global thread
# option set to "1:1" first, so the fit itself runs single-threaded. Tests whether the
# run-to-run differences between identical fits come from INLA's parallel computation
# (CH-20). predict.R passes no num.threads, so inla() takes it from this option; the
# instrumented code is otherwise unchanged. Arguments as for instrument_reference.R.
suppressPackageStartupMessages(library(INLA))
inla.setOption(num.threads = "1:1")
source(file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))),
                 "instrument_reference.R"))
