# dlnm::integer, as installed (dlnm 2.4.10), deparsed
function (x, values, intercept = FALSE) 
{
    nx <- names(x)
    x <- as.vector(x)
    levels <- if (!missing(values)) 
        values
    else sort(unique(x))
    xfac <- factor(x, levels = levels)
    basis <- as.matrix(outer(xfac, levels, "==") + 0L)
    if (ncol(basis) > 1L) {
        if (!intercept) 
            basis <- basis[, -1L, drop = FALSE]
    }
    else intercept <- TRUE
    dimnames(basis) <- list(nx, seq(ncol(basis)))
    attributes(basis) <- c(attributes(basis), list(values = levels, 
        intercept = intercept))
    class(basis) <- c("integer", "matrix")
    return(basis)
}
