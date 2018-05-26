import pandas as pd

left_df = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
right_df = pd.read_csv("../Backbone/COMORBIDITY.csv")

col_list= list(right_df)
col_list.remove('HADM_ID')
right_df['COMORBIDITIES'] = right_df[col_list].sum(axis=1)


merged = pd.merge(left_df, right_df[["HADM_ID","COMORBIDITIES"]], on=["HADM_ID"], how='left')
merged = merged.drop_duplicates()
merged.to_csv("SUM_COMORBIDITIES.csv", index=False)
