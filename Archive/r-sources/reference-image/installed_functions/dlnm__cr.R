# dlnm::cr, as installed (dlnm 2.4.10), deparsed
function (x, df = 10, knots = NULL, intercept = FALSE, fx = FALSE, 
    S = NULL) 
{
    nx <- names(x)
    x <- as.vector(x)
    nax <- is.na(x)
    if (nas <- any(nax)) 
        x <- x[!nax]
    if (is.null(knots)) {
        if (df < 3) 
            stop("'df' must be >=3")
        knots <- quantile(unique(x), seq(0, 1, length = df + 
            !intercept))
    }
    else df <- length(knots) - !intercept
    if (add <- length(unique(x)) < length(knots)) 
        x <- c(seq(min(knots), max(knots), length = length(knots)), 
            x)
    oo <- smooth.construct.cr.smooth.spec(s(x, bs = "cr", k = df + 
        !intercept), data = list(x = x), knots = list(x = knots))
    basis <- oo$X
    if (!intercept) 
        basis <- basis[, -1L, drop = FALSE]
    if (add) 
        basis <- basis[-seq(length(knots)), , drop = FALSE]
    if (nas) {
        nmat <- matrix(NA, length(nax), ncol(basis))
        nmat[!nax, ] <- basis
        basis <- nmat
    }
    if (fx) {
        S <- NULL
    }
    else if (is.null(S)) {
        S <- oo$S[[1]]
        S <- (S + t(S))/2
        if (!intercept) 
            S <- S[-1L, -1L, drop = FALSE]
    }
    else if (any(dim(S) != ncol(basis))) 
        stop("dimensions of 'S' not compatible")
    dimnames(basis) <- list(nx, seq(ncol(basis)))
    attributes(basis) <- c(attributes(basis), list(df = df, knots = knots, 
        intercept = intercept, fx = fx, S = S))
    class(basis) <- c("cr", "matrix")
    return(basis)
}
