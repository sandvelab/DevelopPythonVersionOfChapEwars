# INLA::inla.scale.model, as installed (INLA 25.10.19), deparsed
function (Q, constr = NULL, eps = sqrt(.Machine$double.eps)) 
{
    res <- inla.scale.model.internal(Q = Q, constr = constr, 
        eps = eps)
    return(res$Q)
}
