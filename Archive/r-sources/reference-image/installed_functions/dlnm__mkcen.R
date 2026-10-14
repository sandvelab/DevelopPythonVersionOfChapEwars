# dlnm::mkcen, as installed (dlnm 2.4.10), deparsed
function (cen, type, basis, range) 
{
    if (nocen <- is.null(cen)) 
        cen <- switch(type, cb = attributes(basis)$argvar$cen, 
            one = attributes(basis)$cen, gam = NULL)
    fun <- switch(type, cb = attributes(basis)$argvar$fun, one = attributes(basis)$fun, 
        gam = basis$margin[[1]]$fun)
    if (!is.null(fun) && fun %in% c("thr", "strata", "integer", 
        "lin")) {
        if (is.logical(cen)) 
            cen <- NULL
    }
    else {
        if (is.null(cen) || (is.logical(cen) && cen)) 
            cen <- median(pretty(range))
        if (is.logical(cen) && !cen) 
            cen <- NULL
    }
    int <- switch(type, cb = attributes(basis)$argvar$intercept, 
        one = attributes(basis)$intercept, gam = basis$margin[[1]]$intercept)
    if (is.logical(int) && int) 
        cen <- NULL
    if (nocen && !is.null(cen)) 
        message("centering value unspecified. Automatically set to ", 
            cen)
    return(cen)
}
