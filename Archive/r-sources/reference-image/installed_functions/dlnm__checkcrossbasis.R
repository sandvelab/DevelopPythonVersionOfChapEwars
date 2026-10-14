# dlnm::checkcrossbasis, as installed (dlnm 2.4.10), deparsed
function (argvar, arglag, addarg) 
{
    if (!is.list(argvar)) 
        stop("'argvar' must be a list")
    if (!is.list(arglag)) 
        stop("'arglag' must be a list")
    if (is.null(argvar$fun) && !is.null(argvar$type)) {
        names(argvar)[names(argvar) == "type"] <- "fun"
        assign("argvar", argvar, parent.frame())
        warning("argument 'type' replaced by 'fun'. See ?onebasis")
    }
    if (is.null(arglag$fun) && !is.null(arglag$type)) {
        names(arglag)[names(arglag) == "type"] <- "fun"
        assign("arglag", arglag, parent.frame())
        warning("argument 'type' replaced by 'fun'. See ?onebasis")
    }
    if (any(c("vartype", "vardf", "vardegree", "varknots", "varbound", 
        "varint", "cen", "cenvalue", "maxlag", "lagtype", "lagdf", 
        "lagdegree", "lagknots", "lagbound", "lagint") %in% addarg)) 
        stop("old usage not allowed any more. See ?crossbasis and ?onebasis")
}
