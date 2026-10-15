function (hist_fn, future_fn, preds_fn, config_path) 
{
    config <- parse_config(config_path)
    covariate_names <- config$additional_continuous_covariates
    nlag <- config$n_lags
    precision <- config$precision
    region_seasonal <- config$region_seasonal
    cat("Config: n_lags=", paste(nlag, collapse = ","), " precision=", precision, " region_seasonal=", region_seasonal, "\n")
    cat("Covariates:", paste(covariate_names, collapse = ", "), "\n")
    historic_df <- read.csv(hist_fn)
    future_df <- read.csv(future_fn)
    if (!("disease_cases" %in% colnames(future_df))) {
        future_df$disease_cases <- NA
    }
    if (nrow(historic_df) > 0) {
        df <- rbind(historic_df, future_df)
    }
    else {
        df <- future_df
    }
    df <- apply_adapters(df)
    if (!("ID_year" %in% colnames(df))) {
        df$ID_year <- as.integer(substr(df$time_period, 1, 4))
    }
    if (!("week" %in% colnames(df)) && !("month" %in% colnames(df))) {
        if (grepl("W", df$time_period[1])) {
            df$week <- as.integer(sub(".*W", "", df$time_period))
        }
        else {
            df$month <- as.integer(substr(df$time_period, 6, 7))
        }
    }
    if ("week" %in% colnames(df)) {
        df <- mutate(df, ID_time_cyclic = week)
        df <- offset_years_and_weeks(df)
    }
    else {
        df <- mutate(df, ID_time_cyclic = month)
        df <- offset_years_and_months(df)
    }
    df$ID_time_cyclic2 <- df$ID_time_cyclic
    df$ID_year <- df$ID_year - min(df$ID_year) + 1
    if (length(covariate_names) == 0) {
        generated <- generate_bacic_model(df, covariate_names, nlag, region_seasonal)
    }
    else {
        generated <- generate_lagged_model(df, covariate_names, nlag, region_seasonal)
    }
    lagged_formula <- generated$formula
    print(colnames(df))
    df <- generated$data
    print(colnames(df))
    df$ID_spat <- as.integer(as.factor(df$ID_spat))
    .tap_frame(df, lagged_formula)
    .t0 <- proc.time()[["elapsed"]]
    model <- inla(formula = lagged_formula, data = df, family = "nbinomial", offset = log(E), control.inla = list(strategy = "adaptive"), control.compute = list(dic = TRUE, config = TRUE, cpo = TRUE, return.marginals = FALSE), control.fixed = list(correlation.matrix = TRUE, prec.intercept = 1e-04, prec = precision), control.predictor = list(link = 1, compute = TRUE), verbose = F, safe = FALSE)
    .tap_fit(model, proc.time()[["elapsed"]] - .t0)
    casestopred <- df$Cases
    idx.pred <- which(is.na(casestopred))
    mpred <- length(idx.pred)
    s <- 1000
    y.pred <- matrix(NA, mpred, s)
    set.seed(.r_seed)
    xx <- inla.posterior.sample(s, model, seed = .inla_seed)
    xx.s <- inla.posterior.sample.eval(function(idx.pred) c(theta[1], Predictor[idx.pred]), xx, idx.pred = idx.pred)
    .tap_samples(xx, xx.s, df, idx.pred, model)
    for (s.idx in 1:s) {
        xx.sample <- xx.s[, s.idx]
        y.pred[, s.idx] <- rnbinom(mpred, mu = exp(xx.sample[-1]), size = xx.sample[1])
    }
    new.df <- data.frame(time_period = df$time_period[idx.pred], location = df$location[idx.pred], y.pred)
    colnames(new.df) <- c("time_period", "location", paste0("sample_", 0:(s - 1)))
    write.csv(new.df, preds_fn, row.names = FALSE)
    saveRDS(model, file = "model.rds")
    cat("Predictions written to", preds_fn, "\n")
}
