# dlnm::smooth.construct.cb.smooth.spec, as installed (dlnm 2.4.10), deparsed
function (object, data, knots) 
{
    if (length(object$term) != 2L) 
        stop("'cb' smoother only accepts two terms")
    argvar <- object$xt$argvar
    arglag <- object$xt$arglag
    if (object$by != "NA") 
        stop("'by' argument not (yet) applicable with 'cb' smoother")
    term <- object$term
    dim <- length(term)
    k <- object$bs.dim
    k[k < 0] <- 10
    if (length(k) == 1) 
        k <- rep(k, 2)
    bs <- object$xt$bs
    if (is.null(bs)) 
        bs <- "ps"
    else if (!all(bs %in% c("ps", "cr"))) 
        stop("only 'ps' and 'cr' smoothers accepted within 'cb'")
    if (length(bs) == 1) 
        bs <- rep(bs, 2)
    m <- object$p.order
    if (!is.list(m) && length(m) == 1) 
        m <- rep(m, 2)
    fx <- object$fixed
    if (sum(is.na(fx)) || is.null(fx)) 
        fx <- rep(FALSE, 2)
    else if (length(fx) == 1) 
        fx <- rep(fx, 2)
    margin <- dat <- knt <- Xm <- Sm <- list(var = NULL, lag = NULL)
    d <- r <- nr <- rep(0, 2)
    mc <- c(TRUE, FALSE)
    C <- matrix(0, 0, 0)
    for (i in seq(dim)) {
        xtarg <- if (i == 1) 
            argvar
        else arglag
        dat <- data[term[i]]
        knt <- knots[term[i]]
        if (is.null(xtarg)) {
            sobj <- do.call(s, list(as.name(term[i]), k = k[i], 
                fx = fx[i], bs = bs[i], m = m[[i]]))
            margin[[i]] <- if (mc[i]) 
                smoothCon(sobj, dat, knt, absorb.cons = TRUE, 
                  n = length(dat[[1]]))[[1]]
            else smooth.construct(sobj, dat, knt)
            Xm[[i]] <- margin[[i]]$X
            if (!fx[i]) 
                Sm[[i]] <- margin[[i]]$S[[1]]
            d[i] <- ncol(margin[[i]]$X)
            r[i] <- margin[[i]]$rank
            nr[i] <- margin[[i]]$null.space.dim
        }
        else {
            if (i == 2 && (is.null(xtarg$fun) || "intercept" %in% 
                names(formals(xtarg$fun))) && sum(pmatch(names(xtarg), 
                "intercept", nomatch = 0)) == 0) 
                xtarg$intercept <- TRUE
            Xm[[i]] <- do.call("onebasis", modifyList(xtarg, 
                list(x = dat[[term[i]]])))
            attr <- attributes(Xm[[i]])
            ind <- match(c("fun", names(formals(attr$fun))), 
                names(attr), nomatch = 0)
            margin[[i]] <- attr[ind]
            class(margin[[i]]) <- "onebasis"
            if (!attr$fun %in% c("ps", "cr")) 
                fx[i] <- TRUE
            if (!fx[i]) 
                Sm[[i]] <- attr$S
            d[i] <- nr[i] <- ncol(Xm[[i]])
        }
    }
    X <- tensor.prod.model.matrix(unname(Xm))
    S <- list()
    if (!fx[1]) {
        Sm[[1]] <- Sm[[1]]/eigen(Sm[[1]], symmetric = TRUE, only.values = TRUE)$values[1]
        S <- c(S, list(Svar = Sm[[1]] %x% diag(d[2])))
    }
    if (!fx[2]) {
        Sm[[2]] <- Sm[[2]]/eigen(Sm[[2]], symmetric = TRUE, only.values = TRUE)$values[1]
        S <- c(S, list(Slag = diag(d[1]) %x% Sm[[2]]))
    }
    max.rank <- prod(d)
    r <- max.rank * r/d
    r <- r[!fx]
    nr <- prod(nr)
    if (!is.null(object$xt$addSlag)) {
        addS <- mkaddSlag(object$xt$addSlag, d)
        S <- c(S, addS)
        r <- c(r, sapply(addS, findrank))
    }
    for (i in seq(dim)) margin[[i]]$X <- margin[[i]]$S <- NULL
    ret <- list(margin = margin, term = term, by = object$by, 
        fx = fx, label = object$label, dim = dim, mp = TRUE, 
        np = FALSE, id = object$id, sp = object$sp, inter = TRUE, 
        mc = mc, plot.me = FALSE, X = X, S = S, C = C, df = ncol(X), 
        null.space.dim = nr, rank = r, XP = list())
    ret$lag <- range(data[[term[2]]])
    class(ret) <- c("cb.smooth", "tensor.smooth")
    return(ret)
}
