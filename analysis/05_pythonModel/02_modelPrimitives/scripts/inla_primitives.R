# The INLA values the Python primitives are checked against, computed by the INLA and R the
# reference image ships (INLA 25.10.19, R 4.5.0). Run inside the image (claim.md, Environment).
# Usage: Rscript inla_primitives.R <out dir>
suppressPackageStartupMessages(library(INLA))
out <- commandArgs(trailingOnly = TRUE)[1]
dir.create(out, showWarnings = FALSE, recursive = TRUE)

# 1. scale.model for the cyclic RW1, at the node counts the development data give
#    (12 months; 52 and 53 weeks): the factor inla.scale.model applies to the structure matrix.
sc <- do.call(rbind, lapply(c(12L, 52L, 53L), function(n) {
  R <- INLA:::inla.rw(n, order = 1L, cyclic = TRUE, scale.model = FALSE)
  Rs <- INLA:::inla.rw(n, order = 1L, cyclic = TRUE, scale.model = TRUE)
  data.frame(n = n, factor = Rs[1, 1] / R[1, 1])
}))
write.table(sc, file.path(out, "inla_cyclic_rw1_scale.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)

# 2. The pc.mgamma prior on theta = log(size): INLA's R density of the dispersion a = 1/size
#    (inla.pc.dgamma), transformed to a density in theta: p(theta) = p_a(exp(-theta)) exp(-theta).
theta <- seq(-3, 8, by = 0.25)
pc <- data.frame(theta = theta,
                 log_density = log(inla.pc.dgamma(exp(-theta), lambda = 7)) - theta)
write.table(pc, file.path(out, "inla_pc_mgamma.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)

# 3. The negative-binomial log-likelihood, as R's dnbinom(size, mu) computes it.
set.seed(1)
y <- c(0, 1, 5, 17, 120, 3400, 0, 2)
eta <- c(-2, 0.3, 1.5, 3, 4.5, 8, 1, -0.5)
size <- c(0.4, 1.92, 1.92, 2.9, 10, 1.3, 50, 1e5)
nb <- data.frame(y = y, eta = eta, size = size, loglik = dnbinom(y, size = size, mu = exp(eta), log = TRUE))
write.table(nb, file.path(out, "r_dnbinom.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
cat("done:", out, "\n")
