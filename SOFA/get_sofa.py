import csv
import pandas as pd

left_df = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
right_df = pd.read_csv("../Backbone/SOFA.csv")
merged = pd.merge(left_df, right_df, on=["HADM_ID","ICUSTAY_ID"], how='left')
merged = merged.fillna(0)
merged.drop(columns="SUBJECT_ID", inplace=True)
merged = merged.drop_duplicates()
merged.to_csv("SOFA.csv", index=False)
