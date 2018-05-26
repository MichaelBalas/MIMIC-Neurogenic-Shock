import pandas as pd
import csv
import os


c14  = ('00','01','02','03','04')
short_c14=('0','1','2','3','4')
c57  = ('05','06','07','08','09')
short_c57  = ('5','6','7','8','9')
t16  = ('10','11','12','13','14')
t712 = ('15','16','17','18','19')

c14_2  = ('01','02','03','04')
short_c14_2=('1','2','3','4')
c57_2  = ('05','06','07')
short_c57_2  = ('5','6','7')
c14_3  = ('11','12','13','14')
c57_3 = ('15','16','17')

t16_2 = ('20','21','22','23','24','30','31','32','33','34')
t712_2= ('25','26','27','28','29','35','36','37','38','39')


# Add letters in front for sorting in this order (will remove later)
lvl1="aC1C4"
lvl2="bC5C7"
mult_cerv="cMULTCERV"
cerv="dC1C7"
lvl3="eT1T6"
lvl4="fT7T12"
lumb="gT1T12"
lvl5="hL"

df = pd.read_csv('../Shock_IDs/SHOCK_IDS_ICD.csv')
df['SPINAL_LEVEL'] = 23
df['MULTIPLE_SCI'] = 42
df.to_csv("temp.csv", index=False)


with open('temp.csv', 'rb') as f, open("SPINAL_LEVEL_MULT.csv", 'wb') as outf:
	reader = csv.reader(f, delimiter=',')
	writer = csv.writer(outf)
	for row in reader:
		### Spinal cord injury without evidence of spinal bone injury
		if row[2].startswith('952'):
			if row[2].endswith(c14) or row[2].endswith(short_c14):
				row[3] = lvl1
			elif row[2].endswith(c57) or row[2].endswith(short_c57):
				row[3] = lvl2
			elif row[2].endswith(t16):
				row[3] = lvl3
			elif row[2].endswith(t712):
				row[3] = lvl4
			elif row[2].startswith('9522'):
				row[3] = lvl5
		### Fracture of vertebral column without mention of spinal cord injury
		elif row[2].startswith('805'):
			if row[2].endswith('00') or row[2].endswith('0'):
				row[3] = cerv
			elif row[2].endswith(c14_2) or row[2].endswith(short_c14_2):
				row[3] = lvl1
			elif row[2].endswith(c57_2) or row[2].endswith(short_c57_2):
				row[3] = lvl2
			elif row[2].endswith('08'):
				row[3] = mult_cerv
			elif row[2].endswith('10'):
				row[3] = cerv
			elif row[2].endswith(c14_3):
				row[3] = lvl1
			elif row[2].endswith(c57_3):
				row[3] = lvl2
			elif row[2].endswith('18'):
				row[3] = mult_cerv
			elif row[2].endswith('2') or row[2].endswith('3'):
				row[3] = lumb
			elif row[2].endswith('4') or row[2].endswith('5'):
				row[3] = lvl5
		elif row[2].startswith('806'):
			if row[2].endswith(c14) or row[2].endswith(t16):
				row[3] = lvl1
			elif row[2].endswith(c57) or row[2].endswith(t712):
				row[3] = lvl2
			elif row[2].endswith(t16_2):
				row[3] = lvl3
			elif row[2].endswith(t712_2):
				row[3] = lvl4
			elif row[2].endswith('4') or row[2].endswith('5'):
				row[3] = lvl5
		writer.writerow(row)


df = pd.read_csv("SPINAL_LEVEL_MULT.csv")
# Sort values by HADM_ID and temp (the alphabetical letters make this easier)
df = df.sort_values(by=["HADM_ID", "SPINAL_LEVEL"])
# If there are duplicates (i.e. multiple SCI), write True in MULTIPLE_SCI, else False
df['MULTIPLE_SCI'] = df.duplicated(["HADM_ID"], keep=False)
df = df.drop_duplicates(subset="HADM_ID")
# Remove letters
df['SPINAL_LEVEL'] = df['SPINAL_LEVEL'].str[1:]
df.to_csv("temp2.csv",index=False)

with open('temp2.csv', 'rb') as f, open("SPINAL_LEVEL_MULT.csv", 'wb') as outf:
	reader = csv.reader(f, delimiter=',')
	writer = csv.writer(outf)
	for row in reader:
		### If MULTCERV, then MULTIPLE_SCI=True
		if row[3].startswith('MULT'):
			row[4] = True
			writer.writerow(row)
		else:
			writer.writerow(row)

os.remove('temp.csv')
os.remove('temp2.csv')



