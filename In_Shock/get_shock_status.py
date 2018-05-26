import csv
import pandas as pd
import os

left_df = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
right_df = pd.read_csv("../Backbone/VITALS.csv")
right_df = right_df[["HADM_ID", "ICUSTAY_ID", "HEARTRATE_MEAN", "SYSBP_MEAN"]]
merged = pd.merge(left_df, right_df, on=["HADM_ID","ICUSTAY_ID"], how='left')
merged.insert(4, "IN_SHOCK", "N")
merged = merged.drop_duplicates()
merged.to_csv("merged.csv", index=False)

with open("merged.csv", "rb") as f, open("IN_SHOCK.csv", "wb") as outf:
	reader = csv.reader(f, delimiter=",")
	writer = csv.writer(outf)
	writer.writerow(["HADM_ID", "ICUSTAY_ID", "HEARTRATE_MEAN", "SYSBP_MEAN", "IN_SHOCK"])
	reader.next()
	for row in reader:
		if row[2] in (None, ""):
			if row[3] in (None, ""):
				row[4] = 'NA'
			elif float(row[3]) < 100.00:
				row[4] = 'Y'
			else:
				row[4] = 'N'
		elif row[3] in (None, ""):
			if float(row[2]) < 80.00:
				row[4] = 'Y'
			else:
				row[4] = 'N'
		elif float(row[2]) < 80.00 or float(row[3]) < 100.00:
			row[4] = 'Y'
		else:
			row[4] = 'N'
		writer.writerow(row)

os.remove('merged.csv')



