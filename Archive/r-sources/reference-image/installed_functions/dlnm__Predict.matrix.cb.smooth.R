# dlnm::Predict.matrix.cb.smooth, as installed (dlnm 2.4.10), deparsed
function (object, data) 
{
    term <- object$term
    dim <- length(term)
    Xm <- list()
    for (i in seq(dim)) {
        margin <- object$margin[[i]]
        if (!"onebasis" %in% class(margin)) {
            Xm[[i]] <- if (object$mc[i]) 
                PredictMat(margin, data, n = length(data[[1]]))
            else Predict.matrix(margin, data)
        }
        else {
            Xm[[i]] <- do.call("onebasis", c(list(x = data[[term[i]]]), 
                margin))
        }
    }
    X <- tensor.prod.model.matrix(Xm)
    return(X)
}
