import pandas as pd

shock_ids = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
admission = pd.read_csv("../Backbone/ADMISSION.csv")
dead = pd.merge(shock_ids, admission, on="HADM_ID", how='left')

# If 1, convert to yes, if 2, convert to no
dead.loc[dead['DEAD'] == 1, 'DEAD'] = "Y"
dead.loc[dead['DEAD'] == 2, 'DEAD'] = "N"

# Remove all unnecessary columns
dead = dead[["HADM_ID","ICUSTAY_ID", "DEAD"]]

dead.to_csv("DEAD.csv", index=False)

