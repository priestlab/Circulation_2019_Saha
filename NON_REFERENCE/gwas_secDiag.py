import sys
import csv
import pandas as pd
import numpy as np
import time
from datetime import datetime

line_list = []

reader = pd.ExcelFile("CHD_phenotypes_OriginalMetacat_GWAS_6560.xlsx")
sheets = reader.sheet_names

diseases = {}  # Dictionary of diseases


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


# Iterates through sheets in excel and converts them into dictionaries to access later.
for s in sheets:
    if s == 'ATTRIBUTES':
        c_df = reader.parse(s)
        attrib = dict(zip(c_df.Attribute, c_df.Code))
        attrib_binaries = {}
        for i, row in c_df.iterrows():
            if str(row['Binary']) != 'nan':
                attrib_binaries[row['Attribute']] = row['Binary'].replace(" ", "").split(',')
    elif 'CHD_ICD10' in s[:9]:
        c_df = reader.parse(s)
        if "EXCLUSION" in s:
            icd10_ex_mals = dict(zip(c_df.ICD10, c_df.MALFORMATION))
        elif "_COND_EX" in s:
            icd10_cond = dict(zip(c_df.ICD10, c_df.MALFORMATION))
        else:
            icd10_mals = dict(zip(c_df.ICD10, c_df.MALFORMATION))
    elif 'CHD_ICD9' in s[:8]:
        c_df = reader.parse(s, converters={'ICD9': str})
        if "EXCLUSION" in s:
            icd9_ex_mals = dict(zip(c_df.ICD9, c_df.MALFORMATION))
        elif "_COND_EX" in s:
            icd9_cond = dict(zip(c_df.ICD9, c_df.MALFORMATION))
        else:
            icd9_mals = dict(zip(c_df.ICD9, c_df.MALFORMATION))
    elif 'CHD_OPCS' in s[:8]:
        c_df = reader.parse(s)
        if "EXCLUSION" in s:
            opcs_ex_mals = dict(zip(c_df.OPCS, c_df.MALFORMATION))
        elif "_COND_EX" in s:
            opcs_cond = dict(zip(c_df.OPCS, c_df.MALFORMATION))
        else:
            opcs_mals = dict(zip(c_df.OPCS, c_df.MALFORMATION))
    elif s == 'CHD_CONDITIONAL_EXCLUSIONS':
        c_df = reader.parse(s)
        # Dictionary of malformations whose values are a list of exclusions.
        cond_dict = {}
        for i, row in c_df.iterrows():
            cond_dict[row['MALFORMATION']] = row['EXCLUSION CRITERIA'].replace(" ", "").split(',')
    elif 'CHD_SELFREP_MC_20002' in s[:20]:
        c_df = reader.parse(s, converters={'CODE': int})
        if "EXCLUSION" in s:
            selfrep_mc_ex_mals = dict(zip(c_df.CODE, c_df.MALFORMATION))
        elif "_COND_EX" in s:
            selfrep_mc_cond = dict(zip(c_df.CODE, c_df.MALFORMATION))
        else:
            selfrep_mc_mals = dict(zip(c_df.CODE, c_df.MALFORMATION))
            selfrep_mc_age = dict(zip(c_df.CODE, c_df.AGE))
    elif 'CHD_SELFREP_OP_20004' in s[:20]:
        c_df = reader.parse(s, converters={'CODE': int})
        if "_COND_EX" in s:
            selfrep_op_cond = dict(zip(c_df.CODE, c_df.MALFORMATION))
        else:
            selfrep_op_mals = dict(zip(c_df.CODE, c_df.MALFORMATION))
            selfrep_op_age = dict(zip(c_df.CODE, c_df.AGE))
    elif s == 'CHECK_ASD_PFO':
        c_df = reader.parse(s, converters={'ICD9': str})
        asd_pfo = {'ICD10': c_df['ICD10'].unique(), 'OPCS': c_df['OPCS'].unique(), 'ICD9': c_df['ICD9'].unique()}
    elif s != 'CHD_METACATEGORIES':
        c_df = reader.parse(s, converters={'ICD9': str, 'SELFREP_MC_20002': int, 'SELFREP_OP_20004': int})
        diseases[s] = {'ICD10': c_df['ICD10'].unique(), 'OPCS': c_df['OPCS'].unique(), 'ICD9': c_df['ICD9'].unique(), 'SELFREP_MC_20002': c_df['SELFREP_MC_20002'].unique(), 'SELFREP_OP_20004': c_df['SELFREP_OP_20004'].unique()}


with open('app15860_standard_data_2016Nov19.txt') as f:
    header = f.readline()
    headers = header.split('\t')
    headers[0] = 'app15860_app15860'

   # Creates the field names for each attribute and gets the index
    attrib_index = {}
    for a in attrib:
        underscore_count = str(attrib[a]).count('_')
        if underscore_count == 2:  # Specific Instance and Specific Item in Array
            for h in headers:
                if str(attrib[a]) == h.split('_', 1)[1]:
                    attrib_index[a] = headers.index(h)
        elif underscore_count == 1:  # Entire Array for Specific Instance
            for h in headers:
                if str(attrib[a]) == h.split('_', 1)[1].rsplit('_', 1)[0]:
                    attrib_index[a+'_'+h.split('_')[-1]] = headers.index(h)
        elif underscore_count == 0:  # Entire Array for All Instances
            for h in headers:
                if str(attrib[a]) == h.split('_')[1]:
                    attrib_index[a+'_'+h.split('_', 2)[-1]] = headers.index(h)

    # Gets the indexes for each code-type used for definitions
    icd10_index = []
    for c in ['41202', '41204']:
        for h in headers:
            if c == h.split('_')[1]:
                icd10_index.append(headers.index(h))

    opcs_index = []
    for o in ['41200', '41210']:
        for h in headers:
            if o == h.split('_')[1]:
                opcs_index.append(headers.index(h))

    icd9_index = []
    for c in ['41203', '41205']:
        for h in headers:
            if c == h.split('_')[1]:
                icd9_index.append(headers.index(h))

    # Gets a list of all index tuples (event code, event age)
    selfrep_mc_index = []
    for h in headers:
        if h.split('_')[1] == '20002':
            array_pos = h.split('_', 2)[2] # Grabs "0_0" from n_20002_0_0 for example
            selfrep_mc_index.append((headers.index(h), headers.index('n_20009_'+array_pos)))

    selfrep_op_index = []
    for h in headers:
        if h.split('_')[1] == '20004':
            array_pos = h.split('_', 2)[2] # Grabs "0_0" from n_20004_0_0 for example
            selfrep_op_index.append((headers.index(h), headers.index('n_20011_'+array_pos)))


    fieldnames = ['Patient_ID']
    for a in attrib_index:
        fieldnames.append(a)
    fieldnames.append('CHD')
    fieldnames.append('Confirmed')
    fieldnames.append('COND_Exclude')
    fieldnames.append('Malformation')
    fieldnames.append('No_CHD_Exclude')
    fieldnames.append('Age_At_CHD_SELFREP')
    fieldnames.append('Keep_Mals')
    for d in diseases:
        fieldnames.append(d)


    lines = f.readlines()

    no_chd_exclude = ['THORACIC_AO_DISSECTION', 'ENDOCARDITIS', 'AORTIC_ROOT', 'PULM_HYPERTENSION', 'HEART_TRANSPLANT', 'HCM', 'PERSISTENT_FETAL_CIRCULATION']

    ALL_UKB_COUNT = 0
    COMPLETE_EXCLUSION_COUNT = 0
    CONFIRMED_COUNT = 0
    UNCONFIRMED_COUNT = 0
    CONTROL_COUNT = 0
    UNCONFIRMED_COUNT_2 = 0
    CONTROL_COUNT_2 = 0
    CONFIRMED_COUNT_3 = 0
    CONTROL_COUNT_3 = 0
    CONTROL_COUNT_FURTHER_EXCLUSION = 0

"""
    for e, line in enumerate(lines):
        try:
            # Fix space issue in textfile. 'newline' is a patient row to be added to the output later. Patient ID is added first.
            if " " in line[:9]:
                line = line[:9].replace(" ", "\t")+line[9:]
            line = line.split('\t')
            newline = {'Patient_ID': line[0]}

            for a in attrib_index:
                attrib_0 = line[attrib_index[a]]
                if str(attrib_0) == 'nan':
                    attrib_0 = ''
                if a in attrib_binaries:
                    if str(attrib_binaries[a]) != 'nan' and (attrib_0 in attrib_binaries[a]):
                        newline[a] = 1
                    elif attrib_0 == '':
                        newline[a] = None
                    else:
                        newline[a] = 0
                else:
                    newline[a] = attrib_0

            ALL_UKB_COUNT += 1

            icd10_line = {line[int(i)] for i in icd10_index if line[int(i)] != ''}
            icd9_line = {line[int(i)] for i in icd9_index if line[int(i)] != ''}
            opcs_line = {line[int(i)] for i in opcs_index if line[int(i)] != ''}
            selfrep_mc_line = {int(line[int(i[0])]) for i in selfrep_mc_index if line[int(i[0])] != ''}
            selfrep_op_line = {int(line[int(i[0])]) for i in selfrep_op_index if line[int(i[0])] != ''}

            inc_mal = [icd10_mals[k] for k in (set(icd10_mals.keys())&icd10_line)]
            inc_mal.extend([icd9_mals[k] for k in (set(icd9_mals.keys())&icd9_line)])
            inc_mal.extend([opcs_mals[k] for k in (set(opcs_mals.keys())&opcs_line)])
            inc_mal.extend([selfrep_mc_mals[k] for k in (set(selfrep_mc_mals.keys())&selfrep_mc_line)])
            inc_mal.extend([selfrep_op_mals[k] for k in (set(selfrep_op_mals.keys())&selfrep_op_line)])

            exc_mal = [icd10_ex_mals[k] for k in (set(icd10_ex_mals.keys())&icd10_line)]
            exc_mal.extend([icd9_ex_mals[k] for k in (set(icd9_ex_mals.keys())&icd9_line)])
            exc_mal.extend([opcs_ex_mals[k] for k in (set(opcs_ex_mals.keys())&opcs_line)])
            exc_mal.extend([selfrep_mc_ex_mals[k] for k in (set(selfrep_mc_ex_mals.keys())&selfrep_mc_line)])

            if len(exc_mal) > 0:
                COMPLETE_EXCLUSION_COUNT += 1
                continue

            # cond_mal refers to the exclusion malformations for patients by ICD10, OPCS, and ICD9
            cond_mal = [icd10_cond[k] for k in (set(icd10_cond.keys())&icd10_line)]
            cond_mal.extend([icd9_cond[k] for k in (set(icd9_cond.keys())&icd9_line)])
            cond_mal.extend([opcs_cond[k] for k in (set(opcs_cond.keys())&opcs_line)])
            cond_mal.extend([selfrep_mc_cond[k] for k in (set(selfrep_mc_cond.keys())&selfrep_mc_line)])
            cond_mal.extend([selfrep_op_cond[k] for k in (set(selfrep_op_cond.keys())&selfrep_op_line)])

            # Check if there are only conditional malformations
            only_has_conditional = False

            if len([m for m in inc_mal if ((len(m) > 5) and (m[-5:] == "_COND"))]) == len(inc_mal) and len(inc_mal) > 0:
                only_has_conditional = True

            condition = False

            # cond_dict refers to CHD_CONDITIONAL_EXCLUSIONS sheet
            # where cond is the conditional_malformation and its value is the exclusion criteria
            if only_has_conditional:
                    for cond in cond_dict:
                        # IF the conditional malformation and at least 1 of the corresponding exclusion malformations exists in a patient, the "condition" is True
                         if (len(set(cond_dict[cond])&set(cond_mal)) > 0) and (cond in inc_mal):
                             condition = True
                             inc_mal = [mal for mal in inc_mal if mal != cond]


            newline['COND_Exclude'] = ','.join(cond_mal)

            newline['No_CHD_Exclude'] = len(set(cond_mal)&set(no_chd_exclude)) == 0
            newline['Confirmed'] = 0

            # Splits into buckets of confirmed, unconfirmed and
            if (len(inc_mal) > 0) and (only_has_conditional==False):
                newline['CHD'] = 1
                CONFIRMED_COUNT += 1
                newline['Confirmed'] = 1
            elif only_has_conditional:
                newline['CHD'] = 2
                UNCONFIRMED_COUNT += 1
            else:
                newline['CHD'] = 0
                CONTROL_COUNT += 1

            if only_has_conditional and condition:
                continue
                #newline['CHD'] = 0
                #CONTROL_COUNT_2 += 1
            elif only_has_conditional:
                UNCONFIRMED_COUNT_2 += 1


            # Checks Self-Reported Data and sets CHD=1 if Age Criteria is True for Uncertain CHD Patients

            newline['Age_At_CHD_SELFREP'] = 'NANA'

            if newline['CHD'] == 2:
                selfrep_mals = []
                keep_mals = []

                selfrep_mc_age_tuples = [(line[int(i[0])], line[int(i[1])]) for i in selfrep_mc_index if (line[int(i[0])] != '') and (line[int(i[1])] != '')]
                selfrep_op_age_tuples = [(line[int(i[0])], line[int(i[1])]) for i in selfrep_op_index if (line[int(i[0])] != '') and (line[int(i[1])] != '')]

                for k, v in selfrep_mc_age_tuples:
                    if int(k) in selfrep_mc_age.keys():
                        selfrep_mals.append(selfrep_mc_mals[int(k)])
                        newline['Age_At_CHD_SELFREP'] = v
                        if (float(v) < float(selfrep_mc_age[int(k)])) and (float(v) >= 0) and (v is not None):
                            newline['CHD'] = 1
                            keep_mals.append(selfrep_mc_mals[int(k)])
                for k, v in selfrep_op_age_tuples:
                    if int(k) in selfrep_op_age.keys():
                        selfrep_mals.append(selfrep_op_mals[int(k)])
                        newline['Age_At_CHD_SELFREP'] = v
                        if (float(v) < float(selfrep_op_age[int(k)])) and (float(v) >= 0) and (v is not None):
                            newline['CHD'] = 1
                            keep_mals.append(selfrep_op_mals[int(k)])

                newline['Keep_Mals'] = ','.join(set(keep_mals))

            if newline['CHD'] == 1:
                CONFIRMED_COUNT_3 += 1
            else:
                CONTROL_COUNT_3 += 1
                if newline['No_CHD_Exclude'] == False:
                    CONTROL_COUNT_FURTHER_EXCLUSION += 1

            for d in diseases:
                selfrep_mc = ast_to_codes(selfrep_mc_line, diseases[d]['SELFREP_MC_20002'])
                selfrep_op = ast_to_codes(selfrep_op_line, diseases[d]['SELFREP_OP_20004'])
                newline[d] = 2000

                if (len(ast_to_codes(icd10_line, diseases[d]['ICD10'])) == 0) and (len(ast_to_codes(icd9_line, diseases[d]['ICD9'])) == 0) and (len(ast_to_codes(opcs_line, diseases[d]['OPCS'])) == 0) and (len(selfrep_mc) == 0) and (len(selfrep_op) == 0):
                    newline[d] = 1000

                if len(selfrep_mc) > 0:
                    selfrep_mc_age_tuples = [(line[int(i[0])], line[int(i[1])]) for i in selfrep_mc_index if (line[int(i[0])] != '') and (line[int(i[1])] != '')]
                    for k, v in selfrep_mc_age_tuples:
                        if k in selfrep_mc:
                            if ((float(v) >= 0) and (v is not None) and (float(v) < newline[d])):
                                newline[d] = float(v)

                if len(selfrep_op) > 0:
                    selfrep_op_age_tuples = [(line[int(i[0])], line[int(i[1])]) for i in selfrep_op_index if (line[int(i[0])] != '') and (line[int(i[1])] != '')]
                    for k, v in selfrep_op_age_tuples:
                      if k in selfrep_op:
                          if ((float(v) >= 0) and (v is not None) and (float(v) < newline[d])):
                              newline[d] = float(v)


            newline['Malformation'] = ','.join(set(inc_mal))


            line_list.append(newline)
            if e%25000 == 0:
                print e
        except:
            break

with open('GWAS_6560_Mar1_prehes.csv', 'w') as c_file:
    c_writer = csv.DictWriter(c_file, fieldnames=fieldnames)
    c_writer.writeheader()
    c_writer.writerows(line_list)

print "ALL_UKB_COUNT: " + str(ALL_UKB_COUNT)
print 'COMPLETE_EXCLUSION_COUNT: ' + str(COMPLETE_EXCLUSION_COUNT)
print 'CONFIRMED_COUNT: ' + str(CONFIRMED_COUNT)
print 'UNCONFIRMED_COUNT: ' + str(UNCONFIRMED_COUNT)
print 'CONTROL_COUNT: ' + str(CONTROL_COUNT)
print 'UNCONFIRMED_COUNT_2: ' + str(UNCONFIRMED_COUNT_2)
print 'CONTROL_COUNT_2: ' + str(CONTROL_COUNT_2+CONTROL_COUNT)
print 'CONFIRMED_COUNT_3: ' + str(CONFIRMED_COUNT_3)
print 'CONTROL_COUNT_3: ' + str(CONTROL_COUNT_3)
print 'CONTROL_COUNT_FINAL: ' + str(CONTROL_COUNT_3-CONTROL_COUNT_FURTHER_EXCLUSION)
"""
# Open HES file and translator file
hes_file = pd.read_csv('hes_all_main_sec_diag.csv')
translator = pd.read_table('eid_translator', sep=',')

hes_translated = pd.merge(hes_file, translator, left_on='eid', right_on='app13721')
hes_translated.drop(['eid', 'app13721'], inplace=True, axis=1)
hes_translated.rename(columns={'app15860':'Patient_ID'}, inplace=True)

icd10_cols = [c for c in hes_translated.columns if 'diag_icd10' in c]
icd9_cols = [c for c in hes_translated.columns if 'diag_icd9' in c]
opcs_cols = [c for c in hes_translated.columns if 'oper4' in c]

print icd10_cols
print icd9_cols
print opcs_cols

for c in icd9_cols:
    hes_translated[c] = hes_translated[c].astype('str')

# Open our file
ukb_file = pd.read_csv('GWAS_6560_Mar1_prehes.csv')

print "Translated HES File. All Files Loaded"

# Get all patients where CHD = 2 and merge on patient ID
merge_file = pd.merge(ukb_file[ukb_file['CHD'] == 2][['Patient_ID', 'Year_Of_Birth', 'CHD']], hes_translated, on='Patient_ID')


def get_years(birth_year, *args):
    # Gets the age value at which the event happened
    birth = int(birth_year)
    for a in args:  # args refer to the possible dates
        if str(a) != 'nan':
            # Gets the year of the event date (e.g. 2000-01-01)
            event_year = int(str(a).split('-', 1)[0])
            return event_year - birth_year
    return 100


merge_file['icd_years'] = merge_file.apply(lambda row: get_years(row['Year_Of_Birth'], row['epistart'], row['admidate'], row['epiend'], row['disdate']), axis=1)
merge_file['opcs_years'] = merge_file.apply(lambda row: get_years(row['Year_Of_Birth'], row['epistart'], row['admidate'], row['opdate'], row['epiend'], row['disdate']), axis=1)

print "Translated Years"

# Get first instance of each code
#merge_file = merge_file.groupby([''])

# Check year output
print merge_file.head()


# Iterate through sheets
categories = {}
print sheets
for s in sheets:
    if s=='STROKE':
        c_df = reader.parse(s, converters={'ICD9': str})
        stroke = {'ICD10': c_df['ICD10'].unique(), 'ICD9': c_df['ICD9'].unique()}
    elif s=='CHECK_ASD_PFO':
        c_df = reader.parse(s, converters={'ICD9': str})
        asd_pfo = {'ICD10': c_df['ICD10'].unique(), 'OPCS': c_df['OPCS'].unique(), 'ICD9': c_df['ICD9'].unique()}
    elif 'CHD_SELFREP_MC_20002' == s:
        c_df = reader.parse(s)
        selfrep_mc_age = dict(zip(c_df.MALFORMATION, c_df.AGE))
    elif 'CHD_SELFREP_OP_20004' == s:
        c_df = reader.parse(s)
        selfrep_op_age = dict(zip(c_df.MALFORMATION, c_df.AGE))
    elif 'CHD_ICD10' == s:
        c_df = reader.parse(s)
        icd10 = dict(zip(c_df.ICD10, c_df.MALFORMATION))
    elif 'CHD_ICD9' == s:
        c_df = reader.parse(s, converters={'ICD9': str})
        icd9 = dict(zip(c_df.ICD9, c_df.MALFORMATION))
    elif 'CHD_OPCS' == s:
        c_df = reader.parse(s)
        opcs = dict(zip(c_df.OPCS, c_df.MALFORMATION))
    elif 'CHD_METACATEGORIES' == s:
        c_df = reader.parse(s)
        metacats = dict(zip(c_df.MALFORMATIONS, c_df.METACATEGORY))


age = {}
for k in selfrep_mc_age.keys():
    age[k] = selfrep_mc_age[k]
for k in selfrep_op_age.keys():
    age[k] = selfrep_op_age[k]

def has_mal(row, mal_type):
    # A binary output field that describes if patient has malformation
    if mal_type == 'STROKE':
        for code in stroke['ICD10']:
            if ((str(code) != 'nan') and ('*' in code)):
                for c in icd10_cols:
                    if (str(row[c]) != 'nan'):
                        if (code[:-1] == row[c][:(len(code)-1)]):
                            return row['icd_years']
            elif (str(code) != 'nan'):
                for c in icd10_cols:
                    if code == row[c]:
                        return row['icd_years']
        for code in stroke['ICD9']:
            if ((str(code) != 'nan') and ('*' in code)):
                for c in icd9_cols:
                    if (str(row[c]) != 'nan'):
                        if (code[:-1] == row[c][:(len(code)-1)]):
                            return row['icd_years']
            elif (str(code) != 'nan'):
                for c in icd9_cols:
                    if code == row[c]:
                        return row['icd_years']
    else:
        if any(row[c] in asd_pfo['ICD10'] for c in icd10_cols) or any(row[c] in asd_pfo['ICD9'] for c in icd9_cols):
            return row['icd_years']
        elif any(row[c] in asd_pfo['OPCS'] for c in opcs_cols):
                return row['opcs_years']
    return 404


def check_age(row):
    # Check ICD10
    keep_mals = []

    for c in icd10_cols:
        if row[c] in icd10.keys():
            malformation = icd10[row[c]]
            if malformation in age.keys():
                if row['icd_years'] < int(age[malformation]):
                    keep_mals.append(malformation)
    # Check ICD9
    for c in icd9_cols:
        if row[c] in icd9.keys():
            malformation = icd9[row[c]]
            if malformation in age.keys():
                if row['icd_years'] < int(age[malformation]):
                    keep_mals.append(malformation)

    # Check OPCS
    for c in opcs_cols:
        i = 0
        if row[c] in opcs.keys():
            malformation = opcs[row[c]]
            if malformation in age.keys():
                if row['opcs_years'] < int(age[malformation]):
                    keep_mals.append(malformation)

    return ','.join(keep_mals)

merge_file['has_stroke'] = merge_file.apply(lambda row: has_mal(row, 'STROKE'), axis=1)
merge_file['has_asd_pfo'] = merge_file.apply(lambda row: has_mal(row, 'ASD_PFO'), axis=1)
merge_file['Keep_Mals'] = merge_file.apply(lambda row: check_age(row), axis=1)

# GROUPBY PATIENT_ID HERE
def grouped_df(x):
     return Series(dict(Stroke = x['has_stroke'].min(),
                        ASD_PFO = x['has_asd_pfo'].min(),
                        Keep_Mals = "%s" % ','.join(x['Keep_Mals'])))

grouped_patients = merge_file.groupby('Patient_ID').agg(dict(has_stroke = 'min',
                   has_asd_pfo = 'min',
                   Keep_Mals = lambda x: '%s'%','.join(x))).reset_index()

grouped_patients['Keep_Mals'] = grouped_patients['Keep_Mals'].apply(lambda mals: ','.join({x for x in mals.split(',') if len(x) > 0}))
print grouped_patients.head()

def earliest_age_at_diagnosis(stroke, asd_pfo):

    if asd_pfo != 404:
        if stroke == 404: # If the patient does not have stroke but has ASD/PFO, chd=1
            return 1
        elif stroke > asd_pfo: # If the patient had a stroke after they had asd/pfo, chd=1
                return 1
        else:
            return 0
    else:
        return 0

grouped_patients['ASD_PFO_TRUE'] = grouped_patients.apply(lambda row: earliest_age_at_diagnosis(row['has_stroke'], row['has_asd_pfo']), axis=1)
ukb_file2 = pd.merge(ukb_file, grouped_patients, on='Patient_ID', how='left')
print ukb_file2.columns


ukb_file2['Keep_Mals'] = ukb_file2.apply(lambda row: ','.join({mal for mal in (row['Keep_Mals_x'],row['Keep_Mals_y']) if ((mal != '') and (type(mal)!=float))}), axis=1)
ukb_file2.drop(['Keep_Mals_x', 'Keep_Mals_y'], axis=1, inplace=True)


def reassign_mals(existing_mals, keep_mals, asd_pfo_true):
    if type(existing_mals) != float:
        exist = existing_mals.split(',')
    else:
        return None

    # Make a list of all possible malformations to remove
    if type(keep_mals) != float:
        remove = [mal for mal in age.keys() if mal not in set(keep_mals.split(','))]
        if asd_pfo_true == 0:
            remove.append('ASD_PFO_COND')
    else:
        remove = age.keys()
        if asd_pfo_true == 0:
            remove.append('ASD_PFO_COND')

    # Add malformations to list if (for some reason) the codes do not exist
    # in the original file, but do exist in HES
    inc_mal = [mal for mal in exist if mal not in remove]
    for k in keep_mals.split(','):
        if k not in inc_mal:
            inc_mal.append(k)
    if ((asd_pfo_true == 1) and ('ASD_PFO_COND' not in inc_mal)):
        inc_mal.append('ASD_PFO_COND')

    return ','.join(inc_mal)

ukb_file2['Malformation'] = ukb_file2.apply(lambda row: reassign_mals(row['Malformation'], row['Keep_Mals'], row['ASD_PFO_TRUE']), axis=1)

print ukb_file2['Keep_Mals'].unique()

ukb_file2['CHD'] = ukb_file2.apply(lambda row: 1 if (((type(row['Keep_Mals']) != float) and (row['Keep_Mals'] != '')) or (row['ASD_PFO_TRUE'] == 1) or (row['CHD'] == 1)) else row['CHD'], axis=1)


ukb_file2 = ukb_file2[ukb_file2['CHD'] != 2] # All patients still unconfirmed are discarded


print 'CONFIRMED_COUNT_3: ' + str(len(ukb_file2[ukb_file2['CHD'] == 1]['Patient_ID'].unique()))
print 'CONTROL_COUNT_3: ' + str(len(ukb_file2[ukb_file2['CHD'] == 0]['Patient_ID'].unique()))
print 'CONTROL_COUNT_FINAL: ' + str(len(ukb_file2[(ukb_file2['CHD'] == 0)&(ukb_file2['No_CHD_Exclude']==True)]['Patient_ID'].unique()))

# Append MetaCategory
ukb_file2['MetaCategory'] = ukb_file2['Malformation'].apply(lambda all_mals: ','.join(sorted({metacats[x] for x in all_mals.split(',') if x in metacats.keys()})) if all_mals else None)

ukb_file2.drop(['Keep_Mals', 'COND_Exclude'], axis=1, inplace=True)

ukb_file2[~(ukb_file2['CHD']==0) | ~(ukb_file2['No_CHD_Exclude'] == False)].to_csv("GWAS_6560_Mar1.csv")
