# splines::ns, as installed (splines 4.5.0), deparsed
function (x, df = NULL, knots = NULL, intercept = FALSE, Boundary.knots = range(x)) 
{
    nx <- names(x)
    x <- as.vector(x)
    nax <- is.na(x)
    if (nas <- any(nax)) 
        x <- x[!nax]
    outside <- if (!missing(Boundary.knots)) {
        Boundary.knots <- sort(Boundary.knots)
        (ol <- x < Boundary.knots[1L]) | (or <- x > Boundary.knots[2L])
    }
    else {
        if (length(x) == 1L) 
            Boundary.knots <- x * c(7, 9)/8
        FALSE
    }
    if (mk.knots <- !is.null(df) && is.null(knots)) {
        nIknots <- df - 1L - intercept
        if (nIknots < 0L) {
            nIknots <- 0L
            warning(gettextf("'df' was too small; have used %d", 
                1L + intercept), domain = NA)
        }
        knots <- if (nIknots > 0L) {
            knots <- seq.int(from = 0, to = 1, length.out = nIknots + 
                2L)[-c(1L, nIknots + 2L)]
            quantile(x[!outside], knots, names = FALSE)
        }
    }
    else {
        if (!all(is.finite(knots))) 
            stop("non-finite knots")
        nIknots <- length(knots)
    }
    if (mk.knots && length(knots) && any(lrEq <- range(knots) %in% 
        Boundary.knots)) {
        if (lrEq[1L]) {
            i <- knots == (piv <- Boundary.knots[1L])
            if (all(i)) 
                stop("all interior knots match left boundary knot")
            knots[i] <- knots[i] + (min(knots[knots > piv]) - 
                piv)/8
        }
        if (lrEq[2L]) {
            i <- knots == (piv <- Boundary.knots[2L])
            if (all(i)) 
                stop("all interior knots match right boundary knot")
            knots[i] <- knots[i] - (piv - max(knots[knots < piv]))/8
        }
        warning("shoving 'interior' knots matching boundary knots to inside")
    }
    Aknots <- sort(c(rep(Boundary.knots, 4L), knots))
    if (any(outside)) {
        basis <- array(0, c(length(x), nIknots + 4L))
        if (any(ol)) {
            k.pivot <- Boundary.knots[1L]
            xl <- cbind(1, x[ol] - k.pivot)
            tt <- splineDesign(Aknots, rep(k.pivot, 2L), 4, c(0, 
                1))
            basis[ol, ] <- xl %*% tt
        }
        if (any(or)) {
            k.pivot <- Boundary.knots[2L]
            xr <- cbind(1, x[or] - k.pivot)
            tt <- splineDesign(Aknots, rep(k.pivot, 2L), 4, c(0, 
                1))
            basis[or, ] <- xr %*% tt
        }
        if (any(inside <- !outside)) 
            basis[inside, ] <- splineDesign(Aknots, x[inside], 
                4)
    }
    else basis <- splineDesign(Aknots, x, ord = 4L)
    const <- splineDesign(Aknots, Boundary.knots, ord = 4L, derivs = c(2L, 
        2L))
    if (!intercept) {
        const <- const[, -1, drop = FALSE]
        basis <- basis[, -1, drop = FALSE]
    }
    qr.const <- qr(t(const))
    basis <- as.matrix((t(qr.qty(qr.const, t(basis))))[, -(1L:2L), 
        drop = FALSE])
    n.col <- ncol(basis)
    if (nas) {
        nmat <- matrix(NA, length(nax), n.col)
        nmat[!nax, ] <- basis
        basis <- nmat
    }
    dimnames(basis) <- list(nx, 1L:n.col)
    a <- list(degree = 3L, knots = if (is.null(knots)) numeric() else knots, 
        Boundary.knots = Boundary.knots, intercept = intercept)
    attributes(basis) <- c(attributes(basis), a)
    class(basis) <- c("ns", "basis", "matrix")
    basis
}
