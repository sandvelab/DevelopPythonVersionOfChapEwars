# dlnm::crossbasis, as installed (dlnm 2.4.10), deparsed
function (x, lag, argvar = list(), arglag = list(), group = NULL, 
    ...) 
{
    checkcrossbasis(argvar, arglag, list(...))
    lag <- if (missing(lag)) 
        c(0, NCOL(x) - 1)
    else mklag(lag)
    x <- as.matrix(x)
    dim <- dim(x)
    if (!dim[2] %in% c(1L, diff(lag) + 1L)) 
        stop("NCOL(x) must be equal to 1 (if x is a time series vector), ", 
            "otherwise to the lag period (for x as a matrix of lagged occurrences)")
    basisvar <- do.call("onebasis", modifyList(argvar, list(x = as.numeric(x))))
    if (length(arglag) == 0L || diff(lag) == 0L) 
        arglag <- list(fun = "strata", df = 1, intercept = TRUE)
    if ((is.null(arglag$fun) || "intercept" %in% names(formals(arglag$fun))) && 
        sum(pmatch(names(arglag), "intercept", nomatch = 0)) == 
            0) 
        arglag$intercept <- TRUE
    arglag$cen <- NULL
    basislag <- do.call("onebasis", modifyList(arglag, list(x = seqlag(lag))))
    if (!is.null(group)) 
        checkgroup(group, x, basisvar, lag)
    crossbasis <- matrix(0, nrow = dim[1], ncol = ncol(basisvar) * 
        ncol(basislag))
    for (v in seq(length = ncol(basisvar))) {
        if (dim[2] == 1L) {
            mat <- as.matrix(Lag(basisvar[, v], seqlag(lag), 
                group = group))
        }
        else mat <- matrix(basisvar[, v], ncol = diff(lag) + 
            1)
        for (l in seq(length = ncol(basislag))) {
            crossbasis[, ncol(basislag) * (v - 1) + l] <- mat %*% 
                (basislag[, l])
        }
    }
    cn <- paste0("v", rep(seq(ncol(basisvar)), each = ncol(basislag)), 
        ".l", rep(seq(ncol(basislag)), ncol(basisvar)))
    dimnames(crossbasis) <- list(rownames(x), cn)
    ind <- match(names(formals(attributes(basisvar)$fun)), names(attributes(basisvar)), 
        nomatch = 0)
    argvar <- c(attributes(basisvar)["fun"], attributes(basisvar)[ind])
    ind <- match(names(formals(attributes(basislag)$fun)), names(attributes(basislag)), 
        nomatch = 0)
    arglag <- c(attributes(basislag)["fun"], attributes(basislag)[ind])
    argvar$cen <- attributes(basisvar)$cen
    attributes(crossbasis) <- c(attributes(crossbasis), list(df = c(ncol(basisvar), 
        ncol(basislag)), range = range(x, na.rm = T), lag = lag, 
        argvar = argvar, arglag = arglag))
    if (!is.null(group)) 
        attributes(crossbasis)$group <- length(unique(group))
    class(crossbasis) <- c("crossbasis", "matrix")
    return(crossbasis)
}
