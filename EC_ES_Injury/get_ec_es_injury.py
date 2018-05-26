import csv
import pandas as pd
import os

a = pd.read_csv("../Backbone/DIAGNOSES_ICD.csv")
a = a[["HADM_ID", "SEQ_NUM", "ICD9_CODE"]]
b = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
df = pd.merge(b, a, on='HADM_ID')
df = df.drop_duplicates()
df.insert(4, "EC_ES_INJURY", "N")
df.to_csv("temp1.csv", index=False)

thoracic = ('807', '83961', '83971', '860', '861', '862', '902')
front_of_neck = ('8075', '8076', '874', '900')
abdomen_pelvis = ('863', '864', '865', '866', '867', '868', '902')
spine_no_cord = ('839') # 805 already being analyzed, ignore
pelvic_fracture = ('808', '83942', '83952', '83969', '83979')
femoral_artery = ('9040', '9041')
crush_above_knee = ('92800', '92801', '9288')
amputation_above_knee = ('8972', '8973', '8976', '8977')
popliteal_artery = ('90441')

has_AP= 'Y'

with open('temp1.csv', 'rb') as f, open('temp2.csv', 'wb') as outf:
	reader = csv.reader(f, delimiter=',')
	writer = csv.writer(outf)
	for row in reader:
		### THORACIC
		if row[3].startswith(thoracic):
			row[4] = has_AP

		### FRONT OF NECK
		elif row[3].startswith(front_of_neck):
			row[4] = has_AP

		### ABDOMEN/PELVIS
		elif row[3].startswith(abdomen_pelvis):
			row[4] = has_AP

		### SPINE W/O CORD
		elif row[3].startswith(spine_no_cord): 
			row[4] = has_AP

		### PELVIC FRACTURE
		elif row[3].startswith(pelvic_fracture):
			row[4] = has_AP

		### FEMORAL ARTERY
		elif row[3].startswith(femoral_artery):
			row[4] = has_AP

		### CRUSH ABOVE KNEE
		elif row[3].startswith(crush_above_knee):
			row[4] = has_AP

		### AMPUTATION ABOVE KNEE
		elif row[3].startswith(amputation_above_knee):
			row[4] = has_AP

		### POPLITEAL ARTERY
		elif row[3].startswith(popliteal_artery):
			row[4] = has_AP

		### IF NONE OF THE ABOVE, NOT TOO TOO SERIOUS
		writer.writerow(row)

'''
 --- TAKE ALL HADM_IDS WITH OTHER SEVERE INJURIES ---
'''

with open('temp2.csv', 'rb') as f, open('allyes.csv', 'wb') as outf:
	reader = csv.reader(f, delimiter=',')
	writer = csv.writer(outf)
	for row in reader:
		if row[4] == 'EC_ES_INJURY':
			writer.writerow(row)
		if row[4] == has_AP:
			writer.writerow(row)

'''
 --- GET ALL SCI PATIENTS WITH OTHER SEVERE INJURIES
'''

left_df = pd.read_csv("../Shock_IDs/SHOCK_IDS.csv")
right_df = pd.read_csv("allyes.csv")
left_df = left_df.drop(columns=[])
right_df.drop(columns=['ICUSTAY_ID','SEQ_NUM','ICD9_CODE'], inplace=True)
merged = pd.merge(left_df, right_df, on=['HADM_ID'], how='left')
merged = merged.drop_duplicates()
merged.to_csv("SCI_YES.csv", index=False)

with open('SCI_YES.csv', 'rb') as f, open('EC_ES_INJURY.csv', 'wb') as outf:
	reader = csv.reader(f, delimiter=',')
	writer = csv.writer(outf)
	for row in reader:
		if row[2] in (None, ""):
			row[2] = "N"
		writer.writerow(row)

ec = pd.read_csv("EC_ES_INJURY.csv")
ec.sort_values(["HADM_ID"])
ec.to_csv("EC_ES_INJURY.csv", index=False)

os.remove('temp1.csv')
os.remove('temp2.csv')
os.remove('allyes.csv')
os.remove('SCI_YES.csv')
