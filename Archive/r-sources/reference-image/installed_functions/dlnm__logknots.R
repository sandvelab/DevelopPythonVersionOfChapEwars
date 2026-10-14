# dlnm::logknots, as installed (dlnm 2.4.10), deparsed
function (x, nk = NULL, fun = "ns", df = 1, degree = 3, intercept = TRUE) 
{
    x <- as.vector(x)
    range <- if (length(x) < 3L) 
        mklag(x)
    else range(x, na.rm = TRUE)
    if (diff(range) == 0) 
        stop("range must be >0")
    if (is.null(nk)) {
        fun <- match.arg(fun, c("ns", "bs", "strata"))
        nk <- switch(fun, ns = df - 1 - intercept, bs = df - 
            degree - intercept, strata = df - intercept)
    }
    if (nk < 1) 
        stop("choice of arguments defines no knots")
    knots <- range[1] + exp(((1 + log(diff(range)))/(nk + 1)) * 
        seq(nk) - 1)
    return(knots)
}
