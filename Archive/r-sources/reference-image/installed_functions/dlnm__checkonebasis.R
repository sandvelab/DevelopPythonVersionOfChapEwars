# dlnm::checkonebasis, as installed (dlnm 2.4.10), deparsed
function (fun, args, cen) 
{
    if (!is.character(fun)) 
        stop("'fun' must be a string referring to a function")
    if (all(names(formals(fun)) != "x")) 
        stop("'fun' must contain argument 'x'")
    if (!is.null(args$cen) && !"cen" %in% names(formals(fun))) {
        warning("centering through 'cen' now applied at the prediction stage. See ?crosspred")
        args$cen <- NULL
    }
    if (fun %in% c("ns", "bs") && !is.null(args$bound)) {
        names(args)[names(args) == "bound"] <- "Boundary.knots"
        warning("use the default argument 'Boundary.knots' for fun 'ns'-'bs'")
    }
    if (fun %in% c("hthr", "lthr", "dthr")) {
        args$side <- switch(fun, hthr = "h", lthr = "l", dthr = "d")
        fun <- "thr"
        warning("function 'hthr'-'lthr'-'dthr' replaced by 'thr'. See ?thr")
    }
    if (fun == "thr" && !is.null(args$knots)) {
        names(args)[names(args) == "knots"] <- "thr.value"
        warning("argument 'knots' replaced by 'thr.value' in function thr. See ?thr")
    }
    if (fun == "strata" && !is.null(args$knots)) {
        names(args)[names(args) == "knots"] <- "breaks"
        warning("argument 'knots' replaced by 'breaks' in function strata. See ?strata")
    }
    assign("fun", fun, parent.frame())
    assign("args", args, parent.frame())
    assign("cen", cen, parent.frame())
}
