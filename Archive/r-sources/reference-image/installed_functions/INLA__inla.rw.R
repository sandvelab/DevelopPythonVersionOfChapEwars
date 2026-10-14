# INLA::inla.rw, as installed (INLA 25.10.19), deparsed
function (n, order = 1L, sparse = TRUE, scale.model = FALSE, 
    cyclic = FALSE, diag.add = 0) 
{
    stopifnot(n >= 1L + 2L * order)
    if (scale.model) {
        if (!cyclic) {
            rd <- order
        }
        else {
            if (order == 1L) {
                rd <- 1L
            }
            else {
                rd <- order - 1L
            }
        }
        Q <- inla.rw(n, order = order, sparse = sparse, scale.model = FALSE, 
            cyclic = cyclic)
        fac <- exp(mean(log(diag(inla.ginv(as.matrix(Q), rankdef = rd)))))
        Q <- fac * Q
    }
    else {
        if (!cyclic) {
            U <- diff(diag(n), diff = order)
            Q <- t(U) %*% U
        }
        else {
            m <- 2L * order + 1L
            k <- 1L + order
            U <- diff(diag(m), diff = order)
            U <- t(U) %*% U
            Q <- toeplitz(c(U[k, k:m], rep(0, n - m), U[k, m:(k + 
                1L)]))
        }
    }
    if (diag.add > 0) {
        Q <- Q + diag.add * Diagonal(n)
    }
    return(if (sparse) inla.as.sparse(Q) else Q)
}
