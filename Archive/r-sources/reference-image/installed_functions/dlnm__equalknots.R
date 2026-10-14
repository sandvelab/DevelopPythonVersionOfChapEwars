# dlnm::equalknots, as installed (dlnm 2.4.10), deparsed
function (x, nk = NULL, fun = "ns", df = 1, degree = 3, intercept = FALSE) 
{
    x <- as.vector(x)
    range <- range(x, na.rm = TRUE)
    if (is.null(nk)) {
        fun <- match.arg(fun, c("ns", "bs", "strata"))
        nk <- switch(fun, ns = df - 1 - intercept, bs = df - 
            degree - intercept, strata = df - intercept)
    }
    if (nk < 1) 
        stop("choice of arguments defines no knots")
    knots <- range[1] + (diff(range)/(nk + 1)) * seq(nk)
    return(knots)
}
