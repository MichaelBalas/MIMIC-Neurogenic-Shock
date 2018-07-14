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

predictors = names(subset(shock_data, select=-c(HADM_ID, ICUSTAY_ID, LOS_HOSPITAL, 
                                               LOS_ICU, DEAD, MULTIPLE_SCI, IN_SHOCK, COMORBIDITIES)))
## --- NAGELKERKE R^2 RANKING --- ##
nagelkerke_ranking <- function(model, predictors){
  total_nagel = NagelkerkeR2(model)[["R2"]]
  nagel_decrease = numeric()
  for (predictor in predictors){
    rhs_formula = as.formula(paste("~ . -", predictor))
    excluded_var = NagelkerkeR2(update(model, rhs_formula))[["R2"]]
    delta = total_nagel - excluded_var
    nagel_decrease = c(nagel_decrease, (delta/total_nagel)*100)
  }
  names(nagel_decrease) <- predictors
  par(mar=c(5,13,2,2),lab=c(20,10,7))
  barplot(sort(nagel_decrease), horiz=TRUE, xlim=c(0,50),las=1,
          xlab=expression(paste("Percent Decrease in R"^"2")))
  return(nagel_decrease)
}

nagelkerke_ranking(fit_dead, predictors)

temp_data = data.frame(subset(data, data$IN_SHOCK == 1))
temp_data$LOS_ICU = cut(temp_data$LOS_ICU, breaks=c(0,2,99), right=FALSE, labels=c(0,1))

fitdi_los = glm(formula = LOS_ICU ~ . - HADM_ID - ICUSTAY_ID - LOS_HOSPITAL - DEAD - IN_SHOCK - 
                  MULTIPLE_SCI - COMORBIDITIES, family = binomial, data=temp_data)

nagelkerke_ranking(fitdi_los, predictors)

## --- AUC Ranking --- ##
auc_ranking <- function(model, predictors){
  lhs_formula = toString(rlang::f_lhs(model$formula))
  model_name = toString(match.call()[2])
  formula = as.formula(paste(lhs_formula, " ~ predict(", model_name, ")",sep=""))
  total_auc = auc(formula, data=model$data)
  auc_decrease = numeric()
  for (predictor in predictors){
    rhs_formula = as.formula(paste("~ . -", predictor))
    new_model = update(model, rhs_formula)
    formula = as.formula(paste(lhs_formula, " ~ predict(new_model)",sep=""))
    new_auc = auc(formula, data=model$data)
    delta = total_auc - new_auc
    auc_decrease = c(auc_decrease, (delta/total_auc)*100)
  }
  names(auc_decrease) <- predictors
  par(mar=c(5,13,2,2),lab=c(25,10,7))
  barplot(sort(auc_decrease), horiz=TRUE, xlim=c(-0.5,10.4),las=1,
          xlab="Percent Decrease in AUC")
  return(auc_decrease)
}

sorted_death_predictors = sort(auc_ranking(fit_dead, predictors))
sorted_los_predictors = sort(auc_ranking(fitdi_los, predictors))


#############################################
# Updated version of Sparse Model Creation
# Computing new AUC ranking at each step
model = fitdi_los ### Parameter
predictors = names(sorted_los_predictors) ### Parameter
lhs_formula = toString(rlang::f_lhs(model$formula))
model_name = "fitdi_los" ### Parameter
formula = as.formula(paste(lhs_formula, " ~ predict(", model_name, ")",sep=""))
old_model = model
old_roc = roc(formula, data=model$data)
delong_pvalues = numeric()
print("Complete Model")
print(old_roc$auc)
print(ci(old_roc$auc))
print("delong p-value: NA")
temp = predictors
for (i in 1:(length(predictors)-1)){
  rhs_formula = as.formula(paste("~ . -", temp[1]))
  new_model = update(old_model, rhs_formula)
  new_formula = as.formula(paste(lhs_formula, " ~ predict(new_model)",sep=""))
  new_roc = roc(new_formula, data=model$data)
  p_value = (roc.test(old_roc, new_roc, method = "delong"))$p.value
  delong_pvalues = c(delong_pvalues, p_value)
  new_pred = sort(auc_ranking(new_model, temp[-1]))
  print(paste("Dropped variable: ", temp[1]))
  temp = names(new_pred)
  print(new_roc$auc)
  print(paste("delong p-value: ",p_value))
  print(ci(new_roc$auc))
  old_model = new_model
  old_roc = new_roc
}
#####################################

## --- DeLong Model Selection --- ##
delong_selection <- function(model, predictors){
  lhs_formula = toString(rlang::f_lhs(model$formula))
  model_name = toString(match.call()[2])
  formula = as.formula(paste(lhs_formula, " ~ predict(", model_name, ")",sep=""))
  old_model = model
  old_roc = roc(formula, data=model$data)
  delong_pvalues = numeric()
  for (predictor in predictors){
    rhs_formula = as.formula(paste("~ . -", predictor))
    new_model = update(old_model, rhs_formula)
    new_formula = as.formula(paste(lhs_formula, " ~ predict(new_model)",sep=""))
    new_roc = roc(new_formula, data=model$data)
    p_value = (roc.test(old_roc, new_roc, method = "delong"))$p.value
    print(predictor)
    print(p_value)
    delong_pvalues = c(delong_pvalues, p_value)
    old_model = new_model
    old_roc = new_roc
  }
  return(delong_pvalues)
}

delong_selection(fit_dead, names(sorted_death_predictors))
delong_selection(fitdi_los, names(sorted_los_predictors))

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

bn_death = data.frame(subset(data, data$IN_SHOCK == 1, select = -c(HADM_ID,ICUSTAY_ID,LOS_HOSPITAL,
                                                              LOS_ICU,IN_SHOCK,MULTIPLE_SCI,COMORBIDITIES)))
# Age: <60 ; 60 - 80 ; 80 - 90
# Levels: [0, 60) [60, 80) [80, 90)
bn_death$AGE = cut(bn_death$AGE, breaks=c(0,50,70,90), right=FALSE, labels=FALSE)
bn_death = as.data.frame(lapply(bn_death, as.factor))
res.hc = hc(bn_death)
display_bn(res.hc)
compute_strength(res.hc, bn_death, "BN_death.tsv")

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
compute_strength(res.hc, bn_los, "BN_LOS_ICU.tsv")

## --- Data Dichotomization for RR correlation matrix --- ##
corr_data = data.frame(subset(data, data$IN_SHOCK == 1))
corr_data <- subset(corr_data, select = -c(HADM_ID, ICUSTAY_ID, LOS_HOSPITAL, 
                                           MULTIPLE_SCI, IN_SHOCK, COMORBIDITIES))

# (all data is converted to character and then to numeric as the factor type cannot be used)
# Note that the middle value in these cuts is not left-inclusive (i.e. (0,3,99) means 0-2 and 3-4 for SOFA)
corr_data$LOS_ICU = as.numeric(as.character(cut(corr_data$LOS_ICU, breaks=c(0,2,99), right=FALSE, labels=c(0,1))))
corr_data$AGE = as.numeric(as.character(cut(corr_data$AGE, breaks=c(0,50,99), right=FALSE, labels=c(0,1))))
corr_data$COAGULATION = as.numeric(as.character(cut(corr_data$COAGULATION, breaks=c(0,3,99), right=FALSE, labels=c(0,1))))
corr_data$RESPIRATION = as.numeric(as.character(cut(corr_data$RESPIRATION, breaks=c(0,3,99), right=FALSE, labels=c(0,1))))
corr_data$RENAL = as.numeric(as.character(cut(corr_data$RENAL, breaks=c(0,3,99), right=FALSE, labels=c(0,1))))
corr_data$LIVER = as.numeric(as.character(cut(corr_data$LIVER, breaks=c(0,3,99), right=FALSE, labels=c(0,1))))
# A GCS value of 4 corresponds to a GCS score of 8 or less.
corr_data$GCS = as.numeric(as.character(cut(corr_data$GCS, breaks=c(0,4,99), right=FALSE, labels=c(0,1))))
corr_data$SPINAL_LEVEL = as.numeric(as.character(cut(as.numeric(corr_data$SPINAL_LEVEL), breaks=c(0,2,99), right=FALSE, labels=c(1,0))))

## --- Co-Occurance Matrix --- ##
# Relative Risk Co-Occurance Matrix
rr = matrix(ncol = length(corr_data), nrow = length(corr_data))
rownames(rr) = c(names(corr_data))
colnames(rr) = c(names(corr_data))
# Prevalence Matrix
s = matrix(ncol = length(corr_data), nrow = length(corr_data))
rownames(s) = c(names(corr_data))
colnames(s) = c(names(corr_data))

for (i in 1:ncol(corr_data)){
  for (j in 1:ncol(corr_data)){
    s[i,j] = count(corr_data[,i] & corr_data[,j] == 1)[,2][2]
  }
}

for (i in 1:ncol(corr_data)){
  for (j in 1:ncol(corr_data)){
    if (i == j){
      rr[i,j] = 0
    } else {
      rr[i,j] = s[i,j]*nrow(corr_data)/(s[i,i]*s[j,j])
    }
  }
}

names1 = NULL
for (i in 1:19) {
  names1 = c(names1,rep(rownames(rr)[i],length(corr_data))) 
  names2 = c(rep(rownames(rr),length(corr_data)))
}

rr = cbind(names1, names2, as.numeric(as.vector(rr)))

index = numeric()
# To drop duplicates (e.g. AGE -> AGE, GENDER -> GENDER, etc..)
for (i in 1:nrow(rr)){
  if (rr[i,1] == rr[i,2]){
    index = c(index, i)
  }
}
# Removes all duplicate node rows by index
rr = rr[-c(index), ]

index = numeric()
# To drop double connections (e.g. AGE -> GENDER & GENDER -> AGE, etc..)
for (i in 1:(nrow(rr)-1)){
  for (j in (i+1):nrow(rr)){
    if (rr[i,1] == rr[j,2] & rr[i,2] == rr[j,1]){
      # Choice of i or j only changes order of removal
      # Choosing j as the index removes the second instance of a duplicate
      # i removes the first instance
      index = c(index, j)
    }
  }
}
# Removes all duplicate edge rows by index
rr = rr[-c(index), ]
# Convert all NAs to zero
rr[is.na(rr)] <- 0

# For Cytoscape
colnames(rr) <- c("Source", "Target", "Strength")  # Rename columns
rr = rr[,c("Source", "Strength", "Target")]  # Rearrange now renamed columns

rr = as.data.frame(rr)

write.table(rr, file = "rr.tsv",quote=FALSE, sep='\t', row.names = FALSE)
write.table(diag(s), file = "prevalence.tsv",quote=FALSE, sep='\t', row.names = TRUE)
