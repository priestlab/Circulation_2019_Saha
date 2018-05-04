import sys
import csv
import pandas as pd
import numpy as np
import time

cardiac_surgery_df = pd.ExcelFile("Cardiac_surgery_codes_Apr6.xlsx")
sheets = cardiac_surgery_df.sheet_names

for s in sheets:
    c_df = cardiac_surgery_df.parse(s)
    if s == 'SELFREP_OP_20004':
        cardiac_surgery_selfrep = set(c_df['CODE'].unique())
    elif s == 'OPCS_41200_41210':
        cardiac_surgery_opcs = set(c_df['OPCS'].unique())


def ast_to_codes(patient_codes, disease_codes):
    """This function is used to check for disease codes in patients. Asterisks are used as a partial match."""
    matched_codes = []  # Starts out empty

    # Gets all codes that aren't null values
    disease_codes = [str(c) for c in disease_codes if str(c) != 'nan']
    patient_codes = [str(c) for c in patient_codes if str(c) != 'nan']
    for c in disease_codes:
        if '*' in c:
            # Makes sure the first few characters match up (e.g. - I50 and I501 will match for I50*).
            matched_codes.extend([p for p in patient_codes if (c[:-1] == p[:(len(c)-1)])])
        else:
            # Exact match
            matched_codes.extend([p for p in patient_codes if p == c])
    return matched_codes

line_list = []
"""
with open('app15860_standard_data_2016Nov19.txt') as f:
    header = f.readline()
    headers = header.split('\t')
    headers[0] = 'app15860_app15860'

    attrib = {'Sex': 31, 'Year_Of_Birth': 34}
    # Creates the field names for each attribute and gets the index
    attrib_index = {}
    for a in attrib:
        for h in headers:
            if str(attrib[a]) == h.split('_')[1]:
                attrib_index[a] = headers.index(h)

    opcs_index = []
    for o in ['41200', '41210']:
        for h in headers:
            if o == h.split('_')[1]:
                opcs_index.append(headers.index(h))

    selfrep_op_index = []
    for h in headers:
        if h.split('_')[1] == '20004':
            array_pos = h.split('_', 2)[2] # Grabs "0_0" from n_20004_0_0 for example
            selfrep_op_index.append((headers.index(h), headers.index('n_20011_'+array_pos)))

    fieldnames = ['Patient_ID']
    fieldnames.append('Sex')
    fieldnames.append('Year_Of_Birth')
    fieldnames.append('Total_SelfRep_Op')
    fieldnames.append('Total_SelfRep_Cardiac_Op')
    fieldnames.append('Total_SelfRep_Cardiac_Less_Than_18')
    fieldnames.append('NON_CS_SelfRep_First_Age')
    fieldnames.append('CS_SelfRep_First_Age')
    fieldnames.append('Had_Cardiac_Surgery_Code')

    lines = f.readlines()

    for e, line in enumerate(lines):
        try:
            # Fix space issue in textfile. 'newline' is a patient row to be added to the output later. Patient ID is added first.
            if " " in line[:9]:
                line = line[:9].replace(" ", "\t")+line[9:]
            line = line.split('\t')
            newline = {'Patient_ID': line[0]}

            for a in attrib_index:
                newline[a] = line[int(attrib_index[a])]

            selfrep_op = {line[int(i[0])] for i in selfrep_op_index if line[int(i[0])] != ''}
            selfrep_cs_codes = ast_to_codes(selfrep_op, cardiac_surgery_selfrep)

            newline['Total_SelfRep_Op'] = len(selfrep_op)
            newline['Had_Cardiac_Surgery_Code'] = int(len(selfrep_cs_codes) > 0)

            newline['Total_SelfRep_Cardiac_Op'] = len(selfrep_cs_codes)

            try:
                newline['NON_CS_SelfRep_First_Age']= min({line[int(i[1])] for i in selfrep_op_index if ((line[int(i[1])] != '') and (float(line[int(i[1])]) >= 0) and (line[int(i[0])] not in selfrep_cs_codes))})
            except:
                if len(selfrep_op) > len(selfrep_cs_codes):
                    newline['NON_CS_SelfRep_First_Age'] = -1
                else:
                    newline['NON_CS_SelfRep_First_Age'] = None

            try:
                cs_min_ages = {line[int(i[1])] for i in selfrep_op_index if ((line[int(i[1])] != '') and (float(line[int(i[1])]) >= 0) and (line[int(i[0])] in selfrep_cs_codes))}
                newline['Total_SelfRep_Cardiac_Less_Than_18'] = len([val for val in cs_min_ages if float(val) < 18])
                newline['CS_SelfRep_First_Age']= min(cs_min_ages)
            except:
                if len(selfrep_cs_codes) > 0:
                    newline['CS_SelfRep_First_Age'] = -1
                newline['CS_SelfRep_First_Age'] = None

            line_list.append(newline)
            if e%25000 == 0:
                print e
        except:
            break


with open('opcs_age_total_prehes.csv', 'w') as c_file:
    c_writer = csv.DictWriter(c_file, fieldnames=fieldnames)
    c_writer.writeheader()
    c_writer.writerows(line_list)
"""
# Open HES file and translator file
hes_file = pd.read_csv('hes_all_main_sec_diag.csv')
translator = pd.read_table('eid_translator', sep=',')

hes_translated = pd.merge(hes_file, translator, left_on='eid', right_on='app13721')
hes_translated.drop(['eid', 'app13721'], inplace=True, axis=1)
hes_translated.rename(columns={'app15860':'Patient_ID'}, inplace=True)

april_1997 = pd.to_datetime('1997-04-01')

hes_translated = hes_translated[pd.to_datetime(hes_translated['epistart']) >= april_1997]
hes_translated = hes_translated[pd.to_datetime(hes_translated['admidate']) >= april_1997]
hes_translated = hes_translated[pd.to_datetime(hes_translated['opdate']) >= april_1997]
hes_translated = hes_translated[pd.to_datetime(hes_translated['epiend']) >= april_1997]
hes_translated = hes_translated[pd.to_datetime(hes_translated['disdate']) >= april_1997]

opcs_cols = [c for c in hes_translated.columns if 'oper4' in c]

# Open our file
ukb_file = pd.read_csv('opcs_age_total_prehes.csv')

print "Translated HES File. All Files Loaded"


# Get all patients
merge_file = pd.merge(ukb_file[['Patient_ID', 'Sex', 'Year_Of_Birth',  'Total_SelfRep_Op','Total_SelfRep_Cardiac_Op', 'Total_SelfRep_Cardiac_Less_Than_18', 'Had_Cardiac_Surgery_Code', 'NON_CS_SelfRep_First_Age', 'CS_SelfRep_First_Age']], hes_translated, on='Patient_ID')


def get_years(birth_year, *args):
    # Gets the age value at which the event happened
    birth = int(birth_year)
    for a in args:  # args refer to the possible dates
        if str(a) != 'nan':
            # Gets the year of the event date (e.g. 2000-01-01)
            event_year = int(str(a).split('-', 1)[0])
            return event_year - birth_year
    return None

merge_file['NON_CS_HES_First_Age'] = merge_file.apply(lambda row: get_years(row['Year_Of_Birth'], row['epistart'], row['admidate'], row['opdate'], row['epiend'], row['disdate']), axis=1)
merge_file['CS_HES_First_Age'] = merge_file.apply(lambda row: row['NON_CS_HES_First_Age'], axis=1)

print "Translated Years"

# Check year output
print merge_file.head()
unique_dict = {}

def count_codes(row):
    # Check OPCS
    vals = [row[c] for c in opcs_cols if str(row[c]) != 'nan']

    if row['Patient_ID'] not in unique_dict:
        unique_dict[row['Patient_ID']] = set(vals)
    else:
        unique_dict[row['Patient_ID']].update(vals)

    return len(vals)


def had_cardiac_surgery(row):
    vals = {row[c] for c in opcs_cols if str(row[c]) != 'nan'}
    cardiac_vals = ast_to_codes(vals, cardiac_surgery_opcs)
    return len(cardiac_vals)

merge_file['Had_Cardiac_Surgery_Code'] = merge_file['Had_Cardiac_Surgery_Code'].fillna(0)
merge_file['Total_Op_HES'] = merge_file.apply(lambda row: count_codes(row), axis=1)
merge_file['Total_HES_Cardiac_Surgery_Op'] = merge_file.apply(lambda row: had_cardiac_surgery(row), axis=1)

merge_file['Had_Cardiac_Surgery_Code'] = merge_file.apply(lambda row: 2 if (row['Total_HES_Cardiac_Surgery_Op'] > 0) else row['Had_Cardiac_Surgery_Code'], axis=1)

print "Done Total"
merge_file[['Patient_ID', 'Sex', 'Year_Of_Birth', 'Total_SelfRep_Op', 'Total_SelfRep_Cardiac_Op', 'Total_SelfRep_Cardiac_Less_Than_18','NON_CS_SelfRep_First_Age', 'CS_SelfRep_First_Age', 'NON_CS_HES_First_Age', 'CS_HES_First_Age', 'Total_Op_HES', 'Total_HES_Cardiac_Surgery_Op', 'Had_Cardiac_Surgery_Code']].to_csv('temp_opcs_age_total.csv')

merge_file = pd.read_csv('temp_opcs_age_total.csv')
ukb_file = pd.read_csv('opcs_age_total_prehes.csv')

NON_CS_Age_First_Op = merge_file[(merge_file['Total_HES_Cardiac_Surgery_Op'] < merge_file['Total_Op_HES'] )].groupby('Patient_ID')['NON_CS_HES_First_Age'].min().reset_index()
CS_Age_First_Op = merge_file[merge_file['Had_Cardiac_Surgery_Code'] == 2].groupby('Patient_ID')['CS_HES_First_Age'].min().reset_index()
CS_Age_First_Op['Had_Cardiac_Surgery_Code'] = 1


Total_Op_HES_sum = merge_file.groupby('Patient_ID')['Total_Op_HES', 'Total_HES_Cardiac_Surgery_Op'].sum().reset_index()
Total_Less_18_Sum =  merge_file[(merge_file['CS_HES_First_Age'] < 18) == True].groupby('Patient_ID')['Total_HES_Cardiac_Surgery_Op'].sum().reset_index(name='Total_HES_Cardiac_Less_Than_18')
Total_Op_HES_count = merge_file.groupby('Patient_ID')[['Patient_ID', 'Total_Op_HES']].size().reset_index(name='Total_Hospital_Records')

print NON_CS_Age_First_Op.head()
print Total_Less_18_Sum.head()
print CS_Age_First_Op.head()
print Total_Op_HES_sum.head()
print Total_Op_HES_count.head()

total_ops = pd.merge(Total_Op_HES_sum, Total_Op_HES_count, on='Patient_ID', how='left')
total_ops_18 = pd.merge(total_ops, Total_Less_18_Sum, on='Patient_ID', how='left')
non_cs_age_op = pd.merge(total_ops_18, NON_CS_Age_First_Op, on='Patient_ID', how='left')
age_op = pd.merge(non_cs_age_op, CS_Age_First_Op, on='Patient_ID', how='left')
ukb_file3 = pd.merge(ukb_file[['Patient_ID', 'Sex', 'Year_Of_Birth', 'Total_SelfRep_Op', 'Total_SelfRep_Cardiac_Op', 'Total_SelfRep_Cardiac_Less_Than_18', 'NON_CS_SelfRep_First_Age', 'CS_SelfRep_First_Age', 'Had_Cardiac_Surgery_Code']], age_op, on='Patient_ID', how='left')

ukb_file3['Had_Cardiac_Surgery_Code_y'] = ukb_file3['Had_Cardiac_Surgery_Code_y'].fillna(0)
ukb_file3['Had_Cardiac_Surgery_Code'] = ukb_file3.apply(lambda x: 1 if ((x['Had_Cardiac_Surgery_Code_x'] > 0) or (x['Had_Cardiac_Surgery_Code_y']>0)) else 0, axis=1)
ukb_file3.drop(['Had_Cardiac_Surgery_Code_x', 'Had_Cardiac_Surgery_Code_y'], axis=1, inplace=True)

print total_ops.head()
print total_ops_18.head()
print non_cs_age_op.head()
print age_op.head()

print ukb_file3[ukb_file3['CS_HES_First_Age'].isnull()==False].head()
print len(ukb_file3)


def get_dict_val(pid):
    if pid in unique_dict:
        return len(unique_dict[pid])
    else:
        return 0

ukb_file3['Unique_Op_Hes'] = ukb_file3['Patient_ID'].apply(lambda x: get_dict_val(x))

ukb_file3['Total_Hospital_Records'] = ukb_file3['Total_Hospital_Records'].fillna(0)
ukb_file3['Total_Op_HES'] = ukb_file3['Total_Op_HES'].fillna(0)
ukb_file3['Total_HES_Cardiac_Surgery_Op'] = ukb_file3['Total_HES_Cardiac_Surgery_Op'].fillna(0)
ukb_file3['Total_HES_Cardiac_Less_Than_18'] = ukb_file3['Total_HES_Cardiac_Less_Than_18'].fillna(0)
ukb_file3['Unique_Op_Hes'] = ukb_file3['Unique_Op_Hes'].fillna(0)

def get_min_age(x1, x2, y1, y2, total_ops):
    if total_ops == 0:
        available_vals = {v for v in (x1, x2) if ((str(v) != 'nan')&(float(v)>=0))}
    else:
        available_vals = {v for v in (x1, x2, y1, y2) if ((str(v) != 'nan')&(float(v)>=0))}

    try:
        return min(available_vals)
    except:
        return None


ukb_file3['Age_First_Op'] = ukb_file3.apply(lambda row: get_min_age(row['NON_CS_SelfRep_First_Age'], row['CS_SelfRep_First_Age'], row['NON_CS_HES_First_Age'], row['CS_HES_First_Age'], row['Total_Op_HES']), axis=1)
ukb_file3['NON_CS_HES_First_Age'] = ukb_file3.apply(lambda row: None if row['Total_Op_HES'] == 0 else row['NON_CS_HES_First_Age'], axis=1)
ukb_file3['CS_HES_First_Age'] = ukb_file3.apply(lambda row: None if row['Total_Op_HES'] == 0 else row['CS_HES_First_Age'], axis=1)


ukb_file3['CS_First_Age'] = ukb_file3.apply(lambda row: row['CS_SelfRep_First_Age'] if ((row['CS_SelfRep_First_Age'] < row['CS_HES_First_Age']) or (str(row['CS_HES_First_Age']) == 'nan')) else row['CS_HES_First_Age'], axis=1)
ukb_file3['Total_Cardiac_Op'] = ukb_file3['Total_SelfRep_Cardiac_Op'] + ukb_file3['Total_HES_Cardiac_Surgery_Op']
ukb_file3['Total_Cardiac_Op_Less_Than_18'] = ukb_file3['Total_SelfRep_Cardiac_Less_Than_18'] + ukb_file3['Total_HES_Cardiac_Less_Than_18']


ukb_file3.to_csv("OPCS_Age_and_Total.csv")
