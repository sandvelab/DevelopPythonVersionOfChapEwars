# dlnm::exphist, as installed (dlnm 2.4.10), deparsed
function (exp, times, lag, fill = 0) 
{
    exp <- as.vector(exp)
    lag <- if (missing(lag)) 
        c(0, length(exp) - 1)
    else mklag(lag)
    times <- if (missing(times)) 
        seq(length(exp))
    else round(times)
    left <- max(0, lag[2L] + 1 - min(times))
    right <- max(0, max(times) - length(exp) - lag[1L])
    exp <- c(rep(fill, left), exp, rep(fill, right))
    seqlist <- lapply(times, "-", lag - left)
    hist <- t(sapply(seqlist, function(x) exp[seq(x[1L], x[2L])]))
    dimnames(hist) <- list(times, paste0("lag", seqlag(lag)))
    return(hist)
}
