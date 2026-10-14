# dlnm::summary.onebasis, as installed (dlnm 2.4.10), deparsed
function (object, ...) 
{
    attr <- attributes(object)
    cat("BASIS FUNCTION\n")
    cat("observations:", nrow(object), "\n")
    cat("range:", attr$range, "\n")
    cat("df:", ncol(object), "\n")
    ind <- match(names(formals(attr$fun)), names(attr), nomatch = 0)
    args <- c(list(fun = attr$fun), attr[ind])
    for (i in seq(args)) {
        cat(names(args[i]), ": ", sep = "")
        cat(args[[i]], "\n", sep = " ")
    }
}
