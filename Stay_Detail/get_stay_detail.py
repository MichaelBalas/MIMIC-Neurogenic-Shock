import pandas as pd

left_df = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
right_df = pd.read_csv("../Backbone/STAY_DETAIL.csv")
right_df = right_df[["HADM_ID","ICUSTAY_ID","AGE","GENDER","LOS_HOSPITAL","LOS_ICU"]]
merged = pd.merge(left_df, right_df, on=["HADM_ID","ICUSTAY_ID"], how='left')
merged = merged.drop_duplicates()
merged.to_csv("STAY_DETAIL.csv", index=False)
