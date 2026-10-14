# INLA::inla.posterior.sample, as installed (INLA 25.10.19), deparsed
function (n = 1L, result, selection = list(), intern = FALSE, 
    use.improved.mean = TRUE, skew.corr = TRUE, add.names = TRUE, 
    seed = 0L, num.threads = NULL, parallel.configs = TRUE, verbose = FALSE) 
{
    stopifnot(!missing(result) && inherits(result, "inla"))
    if (is.null(result$misc$configs)) {
        stop("You need an inla-object computed with option \n         'control.compute=list(config = TRUE)'.")
    }
    if (!is.null(result$misc$configs$.preopt) && result$misc$configs$.preopt) {
        rfake <- list(mlik = result$mlik, summary.hyperpar = result$summary.hyperpar, 
            internal.summary.hyperpar = result$internal.summary.hyperpar, 
            misc = list(from.theta = result$misc$from.theta, 
                to.theta = result$misc$to.theta, configs = result$misc$configs))
        rfake$misc$configs$.preopt <- FALSE
        class(rfake) <- "inla"
        ct <- result$misc$configs$contents
        for (nm in c("APredictor", "Predictor")) {
            if (ct$tag[1] == nm) {
                ct$tag <- ct$tag[-1]
                ct$start <- ct$start[-1] - ct$start[2] + 1
                ct$length <- ct$length[-1]
            }
        }
        rfake$misc$configs$contents <- ct
        xx <- inla.posterior.sample(n, rfake, intern = intern, 
            use.improved.mean = use.improved.mean, skew.corr = skew.corr, 
            add.names = add.names, seed = seed, num.threads = num.threads, 
            parallel.configs = parallel.configs, verbose = verbose)
        A <- rbind(result$misc$configs$pA %*% result$misc$configs$A, 
            result$misc$configs$A)
        sel <- inla.posterior.sample.interpret.selection(selection, 
            result)
        if (nrow(result$misc$configs$pA) > 0) {
            pnam <- c(paste0("APredictor:", seq_len(nrow(result$misc$configs$pA))), 
                paste0("Predictor:", seq_len(nrow(result$misc$configs$A))))
        }
        else {
            pnam <- paste0("Predictor:", seq_len(nrow(result$misc$configs$A)))
        }
        cont.A <- NULL
        cont.pA <- NULL
        if (!is.null(result$misc$configs$A)) {
            cont.A <- result$misc$configs$A
        }
        if (!is.null(result$misc$configs$pA)) {
            cont.pA <- result$misc$configs$pA
        }
        attr(xx, ".contents") <- c(result$misc$configs$contents, 
            A = cont.A, pA = cont.pA)
        off <- result$misc$configs$offsets
        for (i in seq_along(xx)) {
            nam <- rownames(xx[[i]]$latent)
            xx[[i]]$latent <- c(as.numeric(A %*% xx[[i]]$latent) + 
                off, as.numeric(xx[[i]]$latent))[sel]
            if (!is.null(nam)) {
                names(xx[[i]]$latent) <- c(pnam, nam)[sel]
            }
            xx[[i]]$latent <- as.matrix(xx[[i]]$latent, ncol = 1)
        }
        return(xx)
    }
    if (is.null(num.threads)) {
        num.threads <- inla.getOption("num.threads")
    }
    if (seed != 0L) {
        num.threads.user <- inla.parse.num.threads(num.threads)
        num.threads <- inla.parse.num.threads("1:1")
        if (num.threads != num.threads.user) {
            warning("Since 'seed!=0', parallel model is disabled and serial model is selected, num.threads='1:1'")
        }
        parallel.configs <- FALSE
    }
    else {
        num.threads <- inla.parse.num.threads(num.threads)
    }
    if (use.improved.mean == FALSE) {
        skew.corr <- FALSE
    }
    if (skew.corr == TRUE && !exists("sn.cache", envir = inla.get.inlaEnv())) {
        inla.create.sn.cache()
    }
    sel <- inla.posterior.sample.interpret.selection(selection, 
        result)
    if (sum(sel) == 0) {
        return(matrix(NA, 0, 0))
    }
    sel.n <- sum(sel)
    sel.map <- which(sel)
    stopifnot(length(sel.map) == sel.n)
    names(sel.map) <- names(sel[sel.map])
    n <- as.integer(n)
    stopifnot(is.integer(n) && n > 0L)
    cs <- result$misc$configs
    ld <- numeric(cs$nconfig)
    for (i in 1:cs$nconfig) {
        ld[i] <- cs$config[[i]]$log.posterior
    }
    p <- exp(ld - max(ld))
    idx <- sort(sample(1:cs$nconfig, n, prob = p, replace = TRUE))
    n.idx <- numeric(cs$nconfig)
    n.idx[] <- 0
    for (i in 1:cs$nconfig) {
        n.idx[i] <- sum(idx == i)
    }
    con <- cs$contents
    all.samples <- rep(list(c()), n)
    i.sample <- 1L
    if (!inla.os("windows") && parallel.configs) {
        nt <- as.numeric(strsplit(num.threads, ":")[[1]])
        ncores <- parallel::detectCores(all.tests = TRUE, logical = FALSE)
        if (nt[1] == 0) {
            nt[1] <- max(1, min(cs$nconfig, ncores))
            nt[2] <- 1
        }
        if (nt[2] == 0) {
            nt[2] <- max(1, ncores%/%nt[1])
        }
        xx.list <- parallel::mclapply(1:cs$nconfig, (function(k) {
            if (n.idx[k] > 0) {
                xx <- inla.qsample(n = n.idx[k], Q = cs$config[[k]]$Q, 
                  mu = inla.ifelse(use.improved.mean, cs$config[[k]]$improved.mean, 
                    cs$config[[k]]$mean), constr = cs$constr, 
                  logdens = TRUE, seed = 0L, num.threads = paste0(nt[2], 
                    ":1"), selection = sel.map, verbose = verbose)
                return(xx)
            }
            else {
                return(NA)
            }
        }), mc.cores = nt[1], mc.preschedule = TRUE)
    }
    else {
        xx.list <- NULL
    }
    for (k in 1:cs$nconfig) {
        if (n.idx[k] > 0) {
            if (is.null(xx.list)) {
                xx <- inla.qsample(n = n.idx[k], Q = cs$config[[k]]$Q, 
                  mu = inla.ifelse(use.improved.mean, cs$config[[k]]$improved.mean, 
                    cs$config[[k]]$mean), constr = cs$constr, 
                  logdens = TRUE, seed = seed, num.threads = num.threads, 
                  selection = sel.map, verbose = verbose)
            }
            else {
                xx <- xx.list[[k]]
            }
            if (seed > 0L) 
                seed <- -1L
            ld.theta <- cs$max.log.posterior + cs$config[[k]]$log.posterior
            nm <- names(sel.map)
            theta <- cs$config[[k]]$theta
            log.J <- 0
            if (!is.null(theta) && !intern) {
                for (j in 1:length(theta)) {
                  theta[j] <- do.call(result$misc$from.theta[[j]], 
                    args = list(theta[j]))
                }
                names(theta) <- inla.transform.names(result, 
                  names(theta))
                if (TRUE) {
                  for (i in 1:length(theta)) {
                    arg.val <- formals(result$misc$from.theta[[i]])
                    arg <- names(arg.val)
                    if (length(arg) == 1L) {
                      deriv.func <- inla.eval(paste("function(", 
                        arg, ") {}"))
                    }
                    else {
                      if (length(arg) == 2L) {
                        deriv.func <- inla.eval(paste("function(", 
                          arg[1L], ",", arg[2L], "=", arg.val[2L], 
                          ") {}"))
                      }
                      else {
                        stopifnot(length(arg) == 3L)
                        deriv.func <- inla.eval(paste("function(", 
                          arg[1L], ",", arg[2L], "=", arg.val[2L], 
                          ",", arg[3L], "=", arg.val[3L], ") {}"))
                      }
                    }
                    temptest <- try(D(body(result$misc$from.theta[[i]]), 
                      arg[1L]), silent = TRUE)
                    if (!inherits(temptest, "try-error")) {
                      body(deriv.func) <- temptest
                      log.J <- log.J - log(abs(deriv.func(cs$config[[k]]$theta[i])))
                    }
                    else {
                      h <- .Machine$double.eps^0.25
                      theta.1 <- do.call(result$misc$from.theta[[i]], 
                        args = list(cs$config[[k]]$theta[i] - 
                          h))
                      theta.2 <- do.call(result$misc$from.theta[[i]], 
                        args = list(cs$config[[k]]$theta[i] + 
                          h))
                      log.J <- log.J - log(abs((theta.2 - theta.1)/(2 * 
                        h)))
                    }
                  }
                }
                else {
                  h <- .Machine$double.eps^0.25
                  for (i in 1:length(theta)) {
                    theta.1 <- do.call(result$misc$from.theta[[i]], 
                      args = list(cs$config[[k]]$theta[i] - h))
                    theta.2 <- do.call(result$misc$from.theta[[i]], 
                      args = list(cs$config[[k]]$theta[i] + h))
                    log.J <- log.J - log(abs((theta.2 - theta.1)/(2 * 
                      h)))
                  }
                }
            }
            if (!skew.corr) {
                sample.corr <- xx$sample
                C.th <- xx$logdens
            }
            else {
                sh.cache <- get("sn.cache", envir = inla.get.inlaEnv())
                dig <- sh.cache$dig
                s <- sh.cache$s
                skew.splines <- sh.cache$skew.splines
                skew.splines.jac <- sh.cache$skew.splines.jac
                speed.fsn <- sh.cache$speed.fsn
                mean.GA <- cs$config[[k]]$mean
                mean.SN <- cs$config[[k]]$improved.mean
                sigma.th <- sqrt(diag(cs$config[[k]]$Qinv))
                val.max <- (mean.GA - mean.SN)/sigma.th
                skew.val <- cs$config[[k]]$skewness
                skew.val[which(is.na(skew.val))] <- 0
                skew.val <- round(skew.val, digits = dig)
                s.new <- round(s, digits = dig)
                skew.table.max <- max(s.new)
                if (any(abs(skew.val) > skew.table.max)) {
                  skew.val <- pmax(-skew.table.max, pmin(skew.table.max, 
                    skew.val))
                  warning(paste0("One or more marginal skewness are too high. Coerced to be ", 
                    skew.table.max))
                }
                zero.not <- which(skew.val != 0)
                if (length(zero.not) == 0 || !any(sel.map %in% 
                  zero.not)) {
                  sample.corr <- xx$sample
                  C.th <- xx$logdens
                }
                else {
                  skew.val.not <- skew.val[zero.not]
                  val.max.not <- val.max[zero.not]
                  dsn.not <- speed.fsn(s = s.new, x = val.max.not, 
                    skew = skew.val.not, fun.splines = skew.splines.jac, 
                    deriv = 1)
                  psn.not <- speed.fsn(s = s.new, x = val.max.not, 
                    skew = skew.val.not, fun.splines = skew.splines.jac)
                  dsn.new <- dnorm(val.max)
                  dsn.new[zero.not] <- dsn.not
                  psn.new <- pnorm(val.max)
                  psn.new[zero.not] <- psn.not
                  if (length(sel.map) < length(skew.val)) {
                    mean.SN <- mean.SN[sel.map]
                    sigma.th <- sigma.th[sel.map]
                    skew.val <- skew.val[sel.map]
                    zero.not <- which(skew.val != 0)
                    if (length(zero.not) != 0) {
                      skew.val.not <- skew.val[zero.not]
                    }
                  }
                  x.sample.not <- xx$sample[zero.not, , drop = FALSE]
                  mean.SN.not <- mean.SN[zero.not]
                  sigma.th.not <- sigma.th[zero.not]
                  x.val.not <- (x.sample.not - mean.SN.not)/sigma.th.not
                  fast.qsn <- speed.fsn(s = s.new, x = x.val.not, 
                    skew = skew.val.not, fun.splines = skew.splines)
                  sample.corr <- xx$sample
                  sample.store <- sigma.th.not * fast.qsn + mean.SN.not
                  sample.corr[zero.not, ] <- sample.store[1:nrow(sample.store), 
                    ]
                  C.th <- xx$logdens + sum(log(dsn.new)) - sum(log(dnorm(qnorm(psn.new))))
                }
            }
            for (i in 1:n.idx[k]) {
                if (is.null(theta)) {
                  a.sample <- list(hyperpar = NULL, latent = sample.corr[, 
                    i, drop = FALSE], logdens = list(hyperpar = NULL, 
                    latent = as.numeric(C.th[i]), joint = as.numeric(C.th[i])))
                }
                else {
                  ld.h <- as.numeric(ld.theta - result$mlik[1, 
                    1] + log.J)
                  a.sample <- list(hyperpar = theta, latent = sample.corr[, 
                    i, drop = FALSE], logdens = list(hyperpar = ld.h, 
                    latent = as.numeric(C.th[i]), joint = as.numeric(ld.h + 
                      C.th[i])))
                }
                if (add.names || i.sample == 1L) {
                  n1 <- length(nm)
                  n2 <- length(a.sample$latent)
                  stopifnot(n2 >= n1)
                  if (n2 > n1) {
                    xnm <- paste0("Lincomb:", inla.num(1:(n2 - 
                      n1)))
                    nm <- c(nm, xnm)
                    if (i.sample == 1L) {
                      con$tag <- c(con$tag, "Lincomb")
                      con$start <- c(con$start, n1 + 1)
                      con$length <- c(con$length, n2 - n1)
                    }
                  }
                  rownames(a.sample$latent) <- nm
                }
                else {
                  rownames(a.sample$latent) <- NULL
                }
                all.samples[[i.sample]] <- a.sample
                i.sample <- i.sample + 1L
            }
        }
    }
    if (length(selection) == 0L) {
        attr(all.samples, ".contents") <- con
    }
    else {
        con <- list(tag = names(selection), start = c(), length = c())
        for (nm in names(selection)) {
            re <- paste0("^", gsub("([.|()\\^{}+$*?]|\\[|\\])", 
                "\\\\\\1", nm), ":")
            m <- grep(re, names(sel.map))
            if (length(m) > 0) {
                con$start <- c(con$start, min(m))
                con$length <- c(con$length, diff(range(m)) + 
                  1)
            }
        }
        attr(all.samples, ".contents") <- con
    }
    return(all.samples)
}
