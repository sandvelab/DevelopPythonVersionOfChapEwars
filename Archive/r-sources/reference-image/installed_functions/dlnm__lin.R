# dlnm::lin, as installed (dlnm 2.4.10), deparsed
function (x, intercept = FALSE) 
{
    nx <- names(x)
    x <- as.vector(x)
    basis <- as.matrix(x)
    if (intercept) 
        basis <- cbind(1, basis)
    dimnames(basis) <- list(nx, seq(ncol(basis)))
    attributes(basis) <- c(attributes(basis), list(intercept = intercept))
    class(basis) <- c("lin", "matrix")
    return(basis)
}
