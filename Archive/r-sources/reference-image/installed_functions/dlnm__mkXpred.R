# dlnm::mkXpred, as installed (dlnm 2.4.10), deparsed
function (type, basis, at, predvar, predlag, cen) 
{
    varvec <- if (is.matrix(at)) 
        as.numeric(at)
    else rep(at, length(predlag))
    lagvec <- rep(predlag, each = length(predvar))
    if (type == "cb") {
        basisvar <- do.call("onebasis", c(list(x = varvec), attr(basis, 
            "argvar")))
        basislag <- do.call("onebasis", c(list(x = lagvec), attr(basis, 
            "arglag")))
        if (!is.null(cen)) {
            basiscen <- do.call("onebasis", c(list(x = cen), 
                attr(basis, "argvar")))
            basisvar <- scale(basisvar, center = basiscen, scale = FALSE)
        }
        Xpred <- tensor.prod.model.matrix(list(basisvar, basislag))
    }
    else if (type == "one") {
        ind <- match(c("fun", names(formals(attr(basis, "fun")))), 
            names(attributes(basis)), nomatch = 0)
        basisvar <- do.call("onebasis", c(list(x = varvec), attributes(basis)[ind]))
        if (!is.null(cen)) {
            basiscen <- do.call("onebasis", c(list(x = cen), 
                attributes(basis)[ind]))
            basisvar <- scale(basisvar, center = basiscen, scale = FALSE)
        }
        Xpred <- basisvar
    }
    else {
        data <- list(varvec, lagvec)
        names(data) <- basis$term
        Xpred <- PredictMat(basis, data, n = length(varvec))
        if (!is.null(cen)) {
            data[[1]] <- rep(cen, length(varvec))
            cbcen <- PredictMat(basis, data, n = length(varvec))
            Xpred <- Xpred - cbcen
        }
    }
    return(Xpred)
}
