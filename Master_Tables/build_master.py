import pandas as pd

df1 = pd.read_csv("../Stay_Detail/STAY_DETAIL.csv")
df2 = pd.read_csv("../Dead/DEAD.csv")
df3 = pd.read_csv("../Spinal_Level_Mult/SPINAL_LEVEL_MULT.csv")
df4 = pd.read_csv("../In_Shock/IN_SHOCK.csv")
df5 = pd.read_csv("../EC_ES_Injury/EC_ES_INJURY.csv")
df6 = pd.read_csv("../Sum_Comorbidities/SUM_COMORBIDITIES.csv")
df7 = pd.read_csv("../SOFA/SOFA.csv")


dfs = [df1, df2, df3, df4, df5, df6, df7]

df_final = reduce(lambda left,right: pd.merge(left,right,on=["HADM_ID","ICUSTAY_ID"]), dfs)
df_final.drop(columns=["ICD9_CODE","HEARTRATE_MEAN","SYSBP_MEAN"], inplace=True)
df_final["IN_SHOCK"] = df_final["IN_SHOCK"].fillna("NA")
df_final.drop(df_final[(df_final.AGE > 89)].index, inplace=True)

### Process the data for linear regression
# FEMALE = 0; MALE = 1
df_final.GENDER = df_final.GENDER.eq('M').mul(1)
# NO = 0; YES = 1
df_final.DEAD = df_final.DEAD.eq('Y').mul(1)
# NO = 0; YES = 1
df_final.drop(df_final[df_final.IN_SHOCK == "NA"].index, inplace=True) # Remove all NAs
df_final.IN_SHOCK = df_final.IN_SHOCK.eq('Y').mul(1)
# NO = 0; YES = 1
df_final.MULTIPLE_SCI = df_final.MULTIPLE_SCI.eq(True).mul(1)
# NO = 0; YES = 1
df_final.EC_ES_INJURY = df_final.EC_ES_INJURY.eq('Y').mul(1)
df_final = df_final.drop_duplicates()

# C1C4, C5C7, C1C7 & MULTCERV = C; T1T6, T7T12 & T1T12 = T; L = L
df_final.loc[df_final['SPINAL_LEVEL'].str.startswith(("C", "M")), 'SPINAL_LEVEL'] = "C"
df_final.loc[df_final['SPINAL_LEVEL'].str.startswith("T"), 'SPINAL_LEVEL'] = "T"


df_final.to_csv("MASTER_ORGAN_FAILURE.csv", index=False)

### Create new Master Table for Comorbidities
df = pd.read_csv("MASTER_ORGAN_FAILURE.csv")
cmb = pd.read_csv("../Backbone/COMORBIDITY.csv")

df.drop(columns=["SOFA","RESPIRATION","COAGULATION","LIVER","CARDIOVASCULAR","CNS","RENAL"], inplace=True)

cmb.columns = map(str.lower, cmb.columns)
cmb.rename(index=str, columns={"hadm_id": "HADM_ID"}, inplace=True)

df = pd.merge(df, cmb, on="HADM_ID", how="left")

### Group Comorbidities Together Into:
### Cardiovascular, Liver-Coag, Pulmonary, Diabetes, Fluid-Electrolyte, Other, Alcohol Abuse

# Cardiovascular: (Congestive heart failure, Cardiac arrhythmias, Valvular disease, Peripheral Vascular Disease, Hypertension, Blood loss anemia, Deficiency anemias)
df.loc[((df.congestive_heart_failure == 1) | (df.cardiac_arrhythmias == 1) | (df.valvular_disease == 1) | (df.peripheral_vascular == 1) | (df.hypertension == 1) | (df.blood_loss_anemia == 1) | (df.deficiency_anemias == 1)), 'CARDIOVASCULAR'] = 1

# Liver: (Liver disease)
df.loc[(df.liver_disease == 1), 'LIVER'] = 1

# Coagulopathy: (Coagulopathy)
df.loc[(df.coagulopathy == 1), 'COAGULOPATHY'] = 1

# Pulmonary: (Pulmonary circulation, Chronic pulmonary)
df.loc[((df.pulmonary_circulation == 1) | (df.chronic_pulmonary)), 'PULMONARY'] = 1

# Diabetes: (Diabetes uncomplicated, Diabetes complicated)
df.loc[((df.diabetes_uncomplicated == 1) | (df.diabetes_complicated == 1)), 'DIABETES'] = 1

# Fluid-Electrolyte: (Fluid electrolyte, Renal failure)
df.loc[((df.fluid_electrolyte == 1) | (df.renal_failure == 1)), 'FLUID_ELECTROLYTE'] = 1

# Other: (Hypothyroidism, Peptic ulcer, Aids, Lymphoma, Rheumatoid arthritis, Obesity, Weight loss, Drug abuse, Psychoses, Depression)
df.loc[((df.hypothyroidism == 1) | (df.peptic_ulcer == 1) | (df.aids == 1) | (df.lymphoma == 1) | (df.rheumatoid_arthritis == 1) | (df.obesity == 1) | (df.weight_loss == 1) | (df.drug_abuse == 1) | (df.psychoses == 1) | (df.solid_tumor == 1) | (df.metastatic_cancer == 1) | (df.depression == 1)), 'OTHER'] = 1

# ALCOHOL ABUSE (move to end)
df.loc[(df.alcohol_abuse == 1), 'ALCOHOL_ABUSE'] = 1

# Drop comorbidity columns ([12-42})
df.drop(df.columns[12:42], axis=1, inplace=True)

df["IN_SHOCK"] = df["IN_SHOCK"].fillna("NA")
df.fillna(0, inplace=True)
df.to_csv("MASTER_COMORBIDITIES.csv", index=False)






