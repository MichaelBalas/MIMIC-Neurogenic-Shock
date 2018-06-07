import pandas as pd

df1 = pd.read_csv("../Stay_Detail/STAY_DETAIL.csv")
df2 = pd.read_csv("../Dead/DEAD.csv")
df3 = pd.read_csv("../Spinal_Level_Mult/SPINAL_LEVEL_MULT.csv")
df4 = pd.read_csv("../In_Shock/IN_SHOCK.csv")
df5 = pd.read_csv("../EC_ES_Injury/EC_ES_INJURY.csv")
df6 = pd.read_csv("../TBI/TBI.csv")
df7 = pd.read_csv("../Sum_Comorbidities/SUM_COMORBIDITIES.csv")
df8 = pd.read_csv("../SOFA/SOFA.csv")

dfs = [df1, df2, df3, df4, df5, df6, df7, df8]

df = reduce(lambda left,right: pd.merge(left,right,on=["HADM_ID","ICUSTAY_ID"]), dfs)
df.drop(columns=["ICD9_CODE","HEARTRATE_MEAN","SYSBP_MEAN"], inplace=True)
df["IN_SHOCK"] = df["IN_SHOCK"].fillna("NA")
df["GCS"] = df["GCS"].fillna("NA")
df.drop(df[(df.AGE > 89)].index, inplace=True)

### Process the data for linear regression
# Remove all NAs
df.drop(df[df.IN_SHOCK == "NA"].index, inplace=True)
df.drop(df[df.GCS == "NA"].index, inplace=True)
# FEMALE = 0; MALE = 1
df.GENDER = df.GENDER.eq('M').mul(1)
# NO = 0; YES = 1
df.DEAD = df.DEAD.eq('Y').mul(1)
# NO = 0; YES = 1
df.IN_SHOCK = df.IN_SHOCK.eq('Y').mul(1)
# NO = 0; YES = 1
df.MULTIPLE_SCI = df.MULTIPLE_SCI.eq(True).mul(1)
# NO = 0; YES = 1
df.EC_ES_INJURY = df.EC_ES_INJURY.eq('Y').mul(1)
df.replace("None", 1, inplace=True)
df.replace("Mild", 2, inplace=True)
df.replace("Moderate", 3, inplace=True)
df.replace("Severe", 4, inplace=True)
df.replace("Vegetative", 4, inplace=True)

df = df.drop_duplicates()

# C1C4, C5C7, C1C7 & MULTCERV = C; T1T6, T7T12 & T1T12 = T; L = L
df.loc[df['SPINAL_LEVEL'].str.startswith(("C", "M")), 'SPINAL_LEVEL'] = "C"
df.loc[df['SPINAL_LEVEL'].str.startswith("T"), 'SPINAL_LEVEL'] = "T"

df.drop(columns=["SOFA", "CARDIOVASCULAR", "CNS"], inplace=True)

### Start Adding Comorbidities
cmb = pd.read_csv("../Backbone/COMORBIDITY.csv")


cmb.columns = map(str.lower, cmb.columns)
cmb.rename(index=str, columns={"hadm_id": "HADM_ID"}, inplace=True)

df = pd.merge(df, cmb, on="HADM_ID", how="left")

### Group Comorbidities Together Into:
### Cardiovascular, Liver-Coag, Pulmonary, Diabetes, Fluid-Electrolyte, Other, Alcohol Abuse

# Cardiovascular: (Congestive heart failure, Cardiac arrhythmias, Valvular disease, Peripheral Vascular Disease, Hypertension, Blood loss anemia, Deficiency anemias, pulmonary circulation)
df.loc[((df.congestive_heart_failure == 1) | (df.cardiac_arrhythmias == 1) | (df.valvular_disease == 1) | (df.peripheral_vascular == 1) | (df.hypertension == 1) | (df.blood_loss_anemia == 1) | (df.deficiency_anemias == 1) | (df.pulmonary_circulation == 1)), 'CMB_CARDIOVASCULAR'] = 1

# Liver/Coagulopathy: (Liver disease, Coagulopathy)
df.loc[((df.liver_disease == 1) | (df.coagulopathy == 1)), 'CMB_LIVER/COAG'] = 1

# Pulmonary: (Chronic pulmonary)
df.loc[(df.chronic_pulmonary == 1), 'CMB_PULMONARY'] = 1

# Diabetes: (Diabetes uncomplicated, Diabetes complicated)
df.loc[((df.diabetes_uncomplicated == 1) | (df.diabetes_complicated == 1)), 'CMB_DIABETES'] = 1

# Fluid-Electrolyte: (Fluid electrolyte, Renal failure)
df.loc[((df.fluid_electrolyte == 1) | (df.renal_failure == 1)), 'CMB_FLUID_ELECTROLYTE'] = 1

# Other: (Hypothyroidism, Peptic ulcer, Aids, Lymphoma, Rheumatoid arthritis, Obesity, Weight loss, Drug abuse, Psychoses, Depression)
df.loc[((df.hypothyroidism == 1) | (df.peptic_ulcer == 1) | (df.aids == 1) | (df.lymphoma == 1) | (df.rheumatoid_arthritis == 1) | (df.obesity == 1) | (df.weight_loss == 1) | (df.drug_abuse == 1) | (df.psychoses == 1) | (df.solid_tumor == 1) | (df.metastatic_cancer == 1) | (df.depression == 1)), 'CMB_OTHER'] = 1

# ALCOHOL ABUSE
df.loc[(df.alcohol_abuse == 1), 'CMB_ALCOHOL_ABUSE'] = 1

# MENTAL HEALTH (Psychoses, Depression)
df.loc[((df.psychoses == 1) | (df.depression == 1)), 'CMB_MENTAL_HEALTH'] = 1

# Drop comorbidity columns ([17-47})
df.drop(df.loc[:,"congestive_heart_failure":"depression"], axis=1, inplace=True)

df.fillna(0, inplace=True)

df.to_csv("MASTER_TABLE.csv", index=False)






