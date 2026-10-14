# dlnm::getvcov, as installed (dlnm 2.4.10), deparsed
function (model, class) 
{
    vcov <- if (any(class %in% c("lm", "glm", "lme", "coxph")) && 
        !identical(class, c("gee", "glm"))) 
        vcov(model)
    else if (identical(class, c("gee", "glm"))) 
        model$robust.variance
    else if (any(class %in% c("lmerMod", "glmerMod", "lmerModLmerTest"))) 
        as.matrix(vcov(model))
    else tryCatch(vcov(model), error = function(w) "error")
    if (identical(vcov, "error")) 
        stop("methods for coef() and vcov() must ", "exist for the class of object 'model'. If not, extract them manually and ", 
            "use the arguments 'coef' and 'vcov'")
    return(vcov)
}
