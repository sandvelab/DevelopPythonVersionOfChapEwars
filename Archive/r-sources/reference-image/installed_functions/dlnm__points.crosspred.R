# dlnm::points.crosspred, as installed (dlnm 2.4.10), deparsed
function (x, ptype, var = NULL, lag = NULL, ci = "n", ci.arg, 
    ci.level = x$ci.level, cumul = FALSE, exp = NULL, ...) 
{
    if (all(class(x) != "crosspred")) 
        stop("'x' must be of class 'crosspred'")
    ci <- match.arg(ci, c("area", "bars", "lines", "n"))
    if (missing(ptype)) {
        if (!is.null(var) || !is.null(lag)) {
            ptype <- "slices"
        }
        else ptype <- "overall"
    }
    ptype <- match.arg(ptype, c("slices", "overall"))
    if (!xor(is.null(var), is.null(lag)) & (ptype == "slices")) {
        stop("One (only) of 'var' or 'lag' must be provided when ptype='slices'")
    }
    if (!is.null(var) && !is.numeric(var) && length(var) > 1 && 
        ptype == "slices") {
        stop("'var' must be a numeric scalar")
    }
    if (!is.null(lag) && !is.numeric(lag) && length(lag) > 1 && 
        ptype == "slices") {
        stop("'lag' must be a numeric scalar")
    }
    if (!is.null(var) && any(!var %in% x$predvar) && (ptype == 
        "slices")) {
        stop("'var' must match values used for prediction")
    }
    if (!is.null(lag) && any(!lag %in% seqlag(x$lag, x$bylag)) && 
        (ptype == "slices")) {
        stop("'lag' must match values used for prediction")
    }
    if (missing(ci.arg)) {
        ci.arg <- list()
    }
    else if (!is.list(ci.arg)) 
        stop("'ci.arg' must be a list")
    if (!is.numeric(ci.level) || ci.level >= 1 || ci.level <= 
        0) {
        stop("'ci.level' must be numeric and between 0 and 1")
    }
    if (cumul == TRUE) {
        x$bylag <- 1
        if (is.null(x$cumfit)) {
            stop("Cumulative outcomes can be plotted if predicted in the 'crosspred'\n  object. Set the argument 'cumul=TRUE' in the function crosspred()")
        }
    }
    if (!is.null(exp) && !is.logical(exp)) 
        stop("'exp' must be logical")
    if (cumul == TRUE) {
        x$matfit <- x$cumfit
        x$matse <- x$cumse
    }
    z <- qnorm(1 - (1 - ci.level)/2)
    x$mathigh <- x$matfit + z * x$matse
    x$matlow <- x$matfit - z * x$matse
    x$allhigh <- x$allfit + z * x$allse
    x$alllow <- x$allfit - z * x$allse
    if ((is.null(exp) && !is.null(x$model.link) && x$model.link %in% 
        c("log", "logit")) || (!is.null(exp) && exp == TRUE)) {
        x$matfit <- exp(x$matfit)
        x$mathigh <- exp(x$mathigh)
        x$matlow <- exp(x$matlow)
        x$allfit <- exp(x$allfit)
        x$allhigh <- exp(x$allhigh)
        x$alllow <- exp(x$alllow)
    }
    if (ptype == "slices") {
        if (!is.null(lag)) {
            xlag <- paste("lag", lag, sep = "")
            plot.arg <- list(type = "p")
            plot.arg <- modifyList(plot.arg, list(...))
            fci(ci = ci, x = x$predvar, high = x$mathigh[, xlag], 
                low = x$matlow[, xlag], ci.arg, plot.arg)
            plot.arg <- modifyList(plot.arg, c(list(x = x$predvar, 
                y = x$matfit[, xlag])))
            do.call("points", plot.arg)
        }
        if (!is.null(var)) {
            xvar <- as.character(var)
            plot.arg <- list(type = "p")
            plot.arg <- modifyList(plot.arg, list(...))
            fci(ci = ci, x = seqlag(x$lag, x$bylag), high = x$mathigh[xvar, 
                ], low = x$matlow[xvar, ], ci.arg, plot.arg)
            plot.arg <- modifyList(plot.arg, c(list(x = seqlag(x$lag, 
                x$bylag), y = x$matfit[xvar, ])))
            do.call("points", plot.arg)
        }
    }
    if (ptype == "overall") {
        plot.arg <- list(type = "p")
        plot.arg <- modifyList(plot.arg, list(...))
        fci(ci = ci, x = x$predvar, high = x$allhigh, low = x$alllow, 
            ci.arg, plot.arg)
        plot.arg <- modifyList(plot.arg, c(list(x = x$predvar, 
            y = x$allfit)))
        do.call("points", plot.arg)
    }
}
