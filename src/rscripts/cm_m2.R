library(mediation)
extract_mediation_summary <- function (x) { 
  
  clp <- 100 * x$conf.level
  isLinear.y <- ((class(x$model.y)[1] %in% c("lm", "rq")) || 
                   (inherits(x$model.y, "glm") && x$model.y$family$family == 
                      "gaussian" && x$model.y$family$link == "identity") || 
                   (inherits(x$model.y, "survreg") && x$model.y$dist == 
                      "gaussian"))
  
  printone <- !x$INT && isLinear.y
  
  if (printone) {
    
    smat <- c(x$d1, x$d1.ci, x$d1.p)
    smat <- rbind(smat, c(x$z0, x$z0.ci, x$z0.p))
    smat <- rbind(smat, c(x$tau.coef, x$tau.ci, x$tau.p))
    smat <- rbind(smat, c(x$n0, x$n0.ci, x$n0.p))
    
    rownames(smat) <- c("ACME", "ADE", "Total Effect", "Prop. Mediated")
    
  } else {
    smat <- c(x$d0, x$d0.ci, x$d0.p)
    smat <- rbind(smat, c(x$d1, x$d1.ci, x$d1.p))
    smat <- rbind(smat, c(x$z0, x$z0.ci, x$z0.p))
    smat <- rbind(smat, c(x$z1, x$z1.ci, x$z1.p))
    smat <- rbind(smat, c(x$tau.coef, x$tau.ci, x$tau.p))
    smat <- rbind(smat, c(x$n0, x$n0.ci, x$n0.p))
    smat <- rbind(smat, c(x$n1, x$n1.ci, x$n1.p))
    smat <- rbind(smat, c(x$d.avg, x$d.avg.ci, x$d.avg.p))
    smat <- rbind(smat, c(x$z.avg, x$z.avg.ci, x$z.avg.p))
    smat <- rbind(smat, c(x$n.avg, x$n.avg.ci, x$n.avg.p))
    
    rownames(smat) <- c("ACME (control)", "ACME (treated)", 
                        "ADE (control)", "ADE (treated)", "Total Effect", 
                        "Prop. Mediated (control)", "Prop. Mediated (treated)", 
                        "ACME (average)", "ADE (average)", "Prop. Mediated (average)")
    
  }
  
  colnames(smat) <- c("Estimate", paste(clp, "% CI Lower", sep = ""), 
                      paste(clp, "% CI Upper", sep = ""), "p-value")
  smat
  
}

args = commandArgs(trailingOnly=TRUE)
output_p <- args[1]
src_p <- args[2]

d_flag <- "cm"
model_flag <- "m2"

data_f <- paste(output_p, "/parameter_data/", d_flag, sep='')
dir.create(data_f, showWarnings = TRUE)

counter_f <- paste(output_p, "/parameter_data/", d_flag, "/", model_flag, "/", sep='')
dir.create(counter_f, showWarnings = TRUE)

data_i <- read.csv(paste(src_p, ".csv", sep = ''))
model.m1 <- lm(X ~ GR - 1, data = data_i)
write.csv(data.frame(summary(model.m1)$coefficients), file=paste(counter_f, "R1_x.csv", sep=''))
model.y1 <- lm(Y ~ X + GR - 1, data = data_i)
write.csv(data.frame(summary(model.y1)$coefficients), file=paste(counter_f, "R1_y.csv", sep=''))

group_list <- c("MB", "FW", "MW") 
for (gi in group_list) {
  med_i <- mediate(model.m1, model.y1, treat='GR', treat.value = gi, control.value = 'FB', mediator='X')
  write.csv(data.frame(extract_mediation_summary(summary(med_i))), file=paste(counter_f, "R1_", gi, "_med.csv", sep=''))
}

print(paste("Done causal model estimation of ", d_flag))

