# dlnm::strata, as installed (dlnm 2.4.10), deparsed
function (x, df = 1, breaks = NULL, ref = 1, intercept = FALSE) 
{
    nx <- names(x)
    x <- as.vector(x)
    range <- range(x, na.rm = TRUE)
    if (!is.null(breaks)) {
        breaks <- sort(unique(breaks))
    }
    else if (df - intercept > 0) 
        breaks <- quantile(x, 1/(df - intercept + 1) * 1:((df - 
            intercept)), na.rm = TRUE)
    df <- length(breaks) + intercept
    xcat <- cut(x, c(range[1] - 1e-04, breaks, range[2] + 1e-04), 
        right = FALSE)
    basis <- matrix(outer(xcat, levels(xcat), "==") + 0, ncol = length(levels(xcat)))
    if (!ref %in% seq(0, ncol(basis))) 
        stop("wrong value in 'ref' argument. See help('strata')")
    if (!intercept && ref == 0) 
        ref <- 1
    if (!is.null(breaks)) {
        if (ref != 0) 
            basis <- basis[, -ref, drop = FALSE]
        if (intercept && ref != 0) 
            basis <- cbind(1, basis)
    }
    dimnames(basis) <- list(nx, seq(ncol(basis)))
    attributes(basis) <- c(attributes(basis), list(df = df, breaks = breaks, 
        ref = ref, intercept = intercept))
    class(basis) <- c("strata", "matrix")
    return(basis)
}
