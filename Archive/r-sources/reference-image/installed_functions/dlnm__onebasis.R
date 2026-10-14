# dlnm::onebasis, as installed (dlnm 2.4.10), deparsed
function (x, fun = "ns", ...) 
{
    nx <- names(x)
    x <- as.vector(x)
    range <- range(x, na.rm = TRUE)
    args <- list(...)
    args$x <- x
    cen <- args$cen
    checkonebasis(fun, args, cen)
    basis <- do.call(fun, args)
    if (is.null(dim(basis))) 
        dim(basis) <- c(length(x), 1)
    attr <- attributes(basis)
    attributes(basis) <- c(list(fun = fun), attr, list(range = range, 
        cen = cen))
    dimnames(basis) <- list(nx, paste("b", seq(ncol(basis)), 
        sep = ""))
    class(basis) <- c("onebasis", "matrix")
    return(basis)
}
