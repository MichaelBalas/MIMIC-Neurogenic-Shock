import pandas as pd

shock_ids = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
oasis = pd.read_csv("../Backbone/OASIS.csv")
tbi = pd.merge(shock_ids, oasis, on=["HADM_ID","ICUSTAY_ID"], how='left')

# Remove all unnecessary columns
tbi = tbi[["HADM_ID","ICUSTAY_ID", "GCS"]]

# If 1, convert to yes, if 2, convert to no

tbi.loc[tbi['GCS'] == 15, 'GCS'] = "None"
tbi.loc[((tbi['GCS'] >= 13) & (tbi['GCS'] < 15)), 'GCS'] = "Mild"
tbi.loc[((tbi['GCS'] >= 9) & (tbi['GCS'] < 13)), 'GCS'] = "Moderate"
tbi.loc[((tbi['GCS'] >= 3) & (tbi['GCS'] < 9)), 'GCS'] = "Severe"
tbi.loc[tbi['GCS'] < 3, 'GCS'] = "Vegetative"


tbi.to_csv("TBI.csv", index=False)


