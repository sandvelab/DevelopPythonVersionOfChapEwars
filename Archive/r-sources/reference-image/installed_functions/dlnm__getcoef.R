# dlnm::getcoef, as installed (dlnm 2.4.10), deparsed
function (model, class) 
{
    coef <- if (any(class %in% c("glm", "gam", "coxph"))) 
        coef(model)
    else if (any(class %in% c("lme", "lmerMod", "glmerMod", "lmerModLmerTest"))) 
        fixef(model)
    else tryCatch(coef(model), error = function(w) "error")
    if (identical(coef, "error")) 
        stop("methods for coef() and vcov() must ", "exist for the class of object 'model'. If not, extract them manually and ", 
            "use the arguments 'coef' and 'vcov'")
    return(coef)
}
