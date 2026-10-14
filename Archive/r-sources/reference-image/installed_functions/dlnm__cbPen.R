# dlnm::cbPen, as installed (dlnm 2.4.10), deparsed
function (cb, sp = -1, addSlag = NULL) 
{
    if (all(class(cb) != "crossbasis") & all(class(cb) != "onebasis")) 
        stop("first argument must be object of class 'crossbasis' or 'onebasis")
    attr <- attributes(cb)
    if (one <- any(class(cb) == "onebasis")) {
        ind <- match(names(formals(attr$fun)), names(attr), nomatch = 0)
        attr <- list(df = c(ncol(cb), 1), range = attr$range, 
            lag = c(0, 0), argvar = c(attr[c("fun", "cen")], 
                attr[ind]), arglag = list(fun = "strata", df = 1, 
                int = TRUE))
    }
    ff <- c(attr$argvar$fun, attr$arglag$fun)
    fx <- c(!ff[1] %in% c("ps", "cr") || attr$argvar$fx, !ff[2] %in% 
        c("ps", "cr") || attr$arglag$fx)
    Slist <- list()
    if (!fx[1]) 
        Slist <- c(Slist, list(Svar = attr$argvar$S %x% diag(attr$df[2])))
    if (!fx[2]) 
        Slist <- c(Slist, list(Slag = diag(attr$df[1]) %x% attr$arglag$S))
    Slist <- lapply(Slist, function(X) X/eigen(X, symmetric = TRUE, 
        only.values = TRUE)$values[1])
    if (one & !is.null(addSlag)) 
        stop("penalties on lag not allowed for class 'onebasis")
    if (!is.null(addSlag)) 
        Slist <- c(Slist, mkaddSlag(addSlag, attr$df))
    rank <- sapply(Slist, findrank)
    npen <- length(Slist)
    if (npen == 0L) 
        stop("no penalization defined")
    if (length(sp) == 1L) 
        sp <- rep(sp, npen)
    if (!is.numeric(sp) || length(sp) != npen) 
        stop("'sp' must be numeric and consistent with number of penalty terms")
    names(sp) <- names(Slist)
    res <- c(Slist, list(rank = rank, sp = sp))
    return(res)
}
