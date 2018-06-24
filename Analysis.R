library(bnlearn)
library(Rgraphviz)
library(fmsb)
library(pROC)

data <- read.csv("Master_Tables/MASTER_TABLE.csv", header=TRUE)
no_shock_data = (subset(data, data$IN_SHOCK == 0))
shock_data = (subset(data, data$IN_SHOCK == 1))

## --- GENERALIZED LINEAR MODELS ---
fit_dead = glm(formula = DEAD ~ . - HADM_ID - ICUSTAY_ID - LOS_HOSPITAL - LOS_ICU - IN_SHOCK - 
                 MULTIPLE_SCI - COMORBIDITIES, family = binomial, data=shock_data)

summary(fit_dead)

fit_los = glm(formula = LOS_ICU ~ . - HADM_ID - ICUSTAY_ID - LOS_HOSPITAL - DEAD - IN_SHOCK - 
                MULTIPLE_SCI - COMORBIDITIES, family = gaussian, data=shock_data)
summary(fit_los)

dead_vars = names(subset(shock_data, select=-c(HADM_ID, ICUSTAY_ID, LOS_HOSPITAL, 
                                               LOS_ICU, DEAD, MULTIPLE_SCI, IN_SHOCK, COMORBIDITIES)))
los_vars = names(subset(shock_data, select=-c(HADM_ID, ICUSTAY_ID, LOS_HOSPITAL, 
                                               LOS_ICU, DEAD, MULTIPLE_SCI, IN_SHOCK, COMORBIDITIES)))
## --- NAGELKERKE R^2 RANKING --- ##
nagelkerke_ranking <- function(model, vars){
  total_nagel = NagelkerkeR2(model)[["R2"]]
  nagel_decrease = numeric()
  for (var in vars){
    rhs_formula = as.formula(paste("~ . -", var))
    excluded_var = NagelkerkeR2(update(model, rhs_formula))[["R2"]]
    delta = total_nagel - excluded_var
    nagel_decrease = c(nagel_decrease, (delta/total_nagel)*100)
  }
  names(nagel_decrease) <- dead_vars
  par(mar=c(5,13,2,2))
  barplot(sort(nagel_decrease), horiz=TRUE, xlim=c(0,max(nagel_decrease)+10),las=1,
          xlab=expression(paste("Percent Decrease in R"^"2")))
  return(nagel_decrease)
}

nagelkerke_ranking(fit_dead, dead_vars)

temp_data = data.frame(subset(data, data$IN_SHOCK == 1))
temp_data$LOS_ICU = cut(temp_data$LOS_ICU, breaks=c(0,2,99), right=FALSE, labels=c(0,1))

fitdi_los = glm(formula = LOS_ICU ~ . - HADM_ID - ICUSTAY_ID - LOS_HOSPITAL - DEAD - IN_SHOCK - 
                  MULTIPLE_SCI - COMORBIDITIES, family = binomial, data=temp_data)

nagelkerke_ranking(fitdi_los, los_vars)


## --- BAYESIAN NETWORKS --- ##

## Displays strength of association between variables
## Plots the strengths by width
## And writes the data to a .tsv file (can be used with Cytoscape)
compute_strength <- function(res, data, path){
  strength = arc.strength(res, data)
  strength.plot(res, strength)
  colnames(strength) <- c("Source", "Target", "Strength")  # Rename columns
  strength = strength[,c("Source", "Strength", "Target")]  # Rearrange now renamed columns
  strength$Strength = strength$Strength * -1.0
  #write.table(strength, file=path, quote=FALSE, sep='\t', row.names = FALSE)
}

## Displays the basic Bayesian Network
display_bn <- function(res){
  # this sets all edges to directed
  g <- Rgraphviz::layoutGraph(bnlearn::as.graphNEL(res))
  # set undirected edges
  u <- names(which(graph::edgeRenderInfo(g)[["direction"]] == "both"))
  graph::edgeRenderInfo(g)[["arrowhead"]][u] = "none"
  graph::edgeRenderInfo(g)[["arrowtail"]][u] = "none"
  # update node attributes: fill colour and label fontsize
  graph::nodeRenderInfo(g) <- list(fill="lightgreen", fontsize=60)
  # render
  Rgraphviz::renderGraph(g)
}

bn_death = data.frame(subset(data, data$IN_SHOCK == 1, select = -c(HADM_ID,ICUSTAY_ID,LOS_HOSPITAL,
                                                              LOS_ICU,IN_SHOCK,MULTIPLE_SCI,COMORBIDITIES)))
# Age: <60 ; 60 - 80 ; 80 - 90
# Levels: [0, 60) [60, 80) [80, 90)
bn_death$AGE = cut(bn_death$AGE, breaks=c(0,50,70,90), right=FALSE, labels=FALSE)
bn_death = as.data.frame(lapply(bn_death, as.factor))
res.hc = hc(bn_death)
display_bn(res.hc)
compute_strength(res.hc, bn_death, "Death_Network/Death_Network.tsv")

bn_los = data.frame(subset(data, data$IN_SHOCK == 1, select = -c(HADM_ID,ICUSTAY_ID,LOS_HOSPITAL,
                                                                   DEAD,IN_SHOCK,MULTIPLE_SCI,COMORBIDITIES)))
bn_los$AGE = cut(bn_los$AGE, breaks=c(0,50,70,90), right=FALSE, labels=FALSE)

# ICU LOS: <2 ; 2-3 ; 4-6 ; 7-13 ; >14
# Levels: [0, 2) [2, 4) [4, 7) [7, 14) [14 99)
bn_los$LOS_ICU = cut(bn_los$LOS_ICU, breaks=c(0,2,7,99), right=FALSE, labels=FALSE)
bn_los <- bn_los[, c("LOS_ICU", setdiff(names(bn_los), "LOS_ICU"))]
bn_los = as.data.frame(lapply(bn_los, as.factor))
res.hc = hc(bn_los)
display_bn(res.hc)
compute_strength(res.hc, bn_los, "LOS_Network/LOS_Network.tsv")

