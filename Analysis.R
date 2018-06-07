library(bnlearn)
library(Rgraphviz)

data <- read.csv("Master_Tables/MASTER_TABLE.csv", header=TRUE)
no_shock_data = (subset(data, data$IN_SHOCK == 0))
shock_data = (subset(data, data$IN_SHOCK == 1))

## --- GENERALIZED LINEAR MODELS ---
fit_dead = glm(formula = DEAD ~ . - HADM_ID - ICUSTAY_ID - LOS_HOSPITAL - LOS_ICU - IN_SHOCK - 
                 MULTIPLE_SCI - COMORBIDITIES, family = binomial, data=shock_data)
summary(fit_dead)

fit_los = glm(formula = LOS_ICU ~ . - HADM_ID - ICUSTAY_ID - LOS_HOSPITAL - DEAD - IN_SHOCK - 
                MULTIPLE_SCI - COMORBIDITIES, family = gaussian, data=shock_data)
summary(fit_dead)


## --- BAYESIAN NETWORKS --- ##

bn_death = data.frame(subset(data, data$IN_SHOCK == 1, select = -c(HADM_ID,ICUSTAY_ID,LOS_HOSPITAL,
                                                              LOS_ICU,IN_SHOCK,MULTIPLE_SCI,COMORBIDITIES)))
# Age: <20 ; 20-24 ; 25-29 ; 30-34 ; 35-44 ; 45-54 ; >55
# Levels: [0, 20) [20, 25) [25, 30) [30, 35) [35, 45) [45, 55) [55, 90)
bn_death$AGE = cut(bn_death$AGE, breaks=c(0,20,25,30,35,45,55,90), right=FALSE, labels=FALSE)
bn_death = as.data.frame(lapply(bn_death, as.factor))
res.hc = hc(bn_death)
display_bn(res.hc)
compute_strength(res.hc, bn_death, "Death_Network/Death_Network.tsv")

bn_los = data.frame(subset(data, data$IN_SHOCK == 1, select = -c(HADM_ID,ICUSTAY_ID,LOS_HOSPITAL,
                                                                   AGE,IN_SHOCK,MULTIPLE_SCI,COMORBIDITIES)))
#bn_los$AGE = cut(bn_los$AGE, breaks=c(0,20,25,30,35,45,55,90), right=FALSE, labels=FALSE)

# ICU LOS: <2 ; 2-3 ; 4-6 ; 7-13 ; >14
# Levels: [0, 2) [2, 4) [4, 7) [7, 14) [14 99)
bn_los$LOS_ICU = cut(bn_los$LOS_ICU, breaks=c(0,2,4,7,14,99), right=FALSE, labels=FALSE)
bn_los <- bn_los[, c("LOS_ICU", setdiff(names(bn_los), "LOS_ICU"))]
bn_los = as.data.frame(lapply(bn_los, as.factor))
res.hc = hc(bn_los)
display_bn(res.hc)
compute_strength(res.hc, bn_los, "LOS_Network/LOS_Network.tsv")

## Displays strength of association between variables
## Plots the strengths by width
## And writes the data to a .tsv file (can be used with Cytoscape)
compute_strength <- function(res, data, path){
  strength = arc.strength(res, data)
  strength.plot(res, strength)
  colnames(strength) <- c("Source", "Target", "Strength")
  strength = strength[,c("Source", "Strength", "Target")]
  strength$Strength = strength$Strength * -1.0
  write.table(strength, file=path, quote=FALSE, sep='\t', row.names = FALSE)
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
