import pandas as pd

### FILTER PATIENTS BY FIRST HOSPITAL ADMISSION AND FIRST ICU STAY

first_hadm_icu = pd.read_csv("../Backbone/STAY_DETAIL.csv")
# Remove all unnecessary columns
first_hadm_icu = first_hadm_icu[["HADM_ID","ICUSTAY_ID", \
					 "FIRST_HOSP_STAY","FIRST_ICU_STAY"]]
# Drop rows where it isn't the first stay for hospital or ICU
first_hadm_icu.drop(first_hadm_icu[(first_hadm_icu.FIRST_HOSP_STAY == "N") | (first_hadm_icu.FIRST_ICU_STAY == "N")].index, inplace=True)
# Don't need stay columns any longer
first_hadm_icu.drop(columns=["FIRST_HOSP_STAY","FIRST_ICU_STAY"], inplace=True)

### FILTER ALL SCI PATIENTS

# ICD9: Spinal cord injury without evidence of spinal bone injury
SCI = ('9520', '9521', '9522')
# ICD9: Fracture of vertebral column without mention of spinal cord injury
Fx_NO_SCI = ('8050', '8051', '8052', '8053', '8054', '8055')
# ICD9: Fracture of vertebral column with spinal cord injury
Fx_SCI = ('8060', '8061', '8062', '8063', '8064', '8065')

sci_ids = pd.read_csv("../Backbone/DIAGNOSES_ICD.csv", converters={"ICD9_CODE":str})
# Remove all unnecessary columns
sci_ids = sci_ids[["HADM_ID","ICD9_CODE"]]

sci_ids = sci_ids[(sci_ids['ICD9_CODE'].str.startswith(SCI)) | (sci_ids['ICD9_CODE'].str.startswith(Fx_NO_SCI)) | (sci_ids['ICD9_CODE'].str.startswith(Fx_SCI))]

shock_ids_icd = pd.merge(first_hadm_icu, sci_ids, on="HADM_ID")
shock_ids = shock_ids_icd.copy()
shock_ids.drop(columns="ICD9_CODE", inplace=True)
shock_ids_icd.to_csv("SHOCK_IDS_ICD.csv", index=False)
shock_ids.to_csv("SHOCK_IDS.csv", index=False)




