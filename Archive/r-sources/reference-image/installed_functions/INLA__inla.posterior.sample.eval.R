# INLA::inla.posterior.sample.eval, as installed (INLA 25.10.19), deparsed
function (fun, samples, return.matrix = TRUE, ...) 
{
    contents <- attr(samples, which = ".contents", exact = TRUE)
    if (is.null(contents)) {
        stop("Argument 'samples' must be the output from 'inla.posterior.sample()'.")
    }
    if (is.character(fun)) {
        arg <- NULL
        for (nm in fun) {
            arg <- paste0(if (is.null(arg)) 
                ""
            else paste0(arg, ","), "get('", nm, "')")
        }
        fun <- inla.eval(paste0("function(...) return(c(", arg, 
            "))"))
    }
    else {
        fun <- match.fun(fun)
    }
    my.fun <- function(a.sample, .contents, .fun, ...) {
        env <- new.env()
        theta <- as.vector(a.sample$hyperpar)
        assign("theta", theta, envir = env)
        if (!is.null(.contents$A)) {
            assign("A", .contents$A, envir = env)
        }
        if (!is.null(.contents$pA)) {
            assign("pA", .contents$pA, envir = env)
        }
        for (i in seq_along(.contents$tag)) {
            assign(.contents$tag[i], as.vector(a.sample$latent[.contents$start[i]:(.contents$start[i] + 
                .contents$length[i] - 1), 1]), envir = env)
        }
        if (exists("(Intercept)", envir = env)) {
            assign("Intercept", get("(Intercept)", envir = env), 
                envir = env)
        }
        parent.env(env) <- .GlobalEnv
        environment(.fun) <- env
        return(.fun(...))
    }
    ret <- inla.mclapply(samples, my.fun, .fun = fun, .contents = contents, 
        ...)
    if (return.matrix) {
        ns <- length(ret)
        nm <- names(ret[[1]])
        ret <- matrix(unlist(ret), ncol = ns)
        colnames(ret) <- paste0("sample:", 1:ns)
        rownames(ret) <- if (!is.null(nm)) 
            nm
        else paste0("fun[", 1:nrow(ret), "]")
    }
    return(ret)
}
