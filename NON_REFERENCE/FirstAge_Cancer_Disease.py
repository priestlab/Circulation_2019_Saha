import sys
import csv
import pandas as pd
import numpy as np
import time

line_list = []

reader = pd.ExcelFile("sensitivity_analyses_for_detection_bias.xlsx")
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
    if ((s != 'Attributes') and (s != 'MI_NO_INTERVENTION')):
        c_df = reader.parse(s, converters={'ICD9': str, 'SELFREP_CANCER_20001': int})
        diseases[s] = {'ICD10': c_df['ICD10'].unique(), 'ICD9': c_df['ICD9'].unique(), 'SELFREP_CANCER_20001': c_df['SELFREP_CANCER_20001'].unique()}


with open('app15860_standard_data_2016Nov19.txt') as f:
    header = f.readline()
    headers = header.split('\t')
    headers[0] = 'app15860_app15860'

    # Gets the indexes for each code-type used for definitions
    icd9_cancer_index = []
    for h in headers:
        if h.split('_')[1] == '40013':
            array_pos = h.split('_', 2)[2] # Grabs "0_0" from n_20002_0_0 for example
            icd9_cancer_index.append((headers.index(h), headers.index('n_40008_'+array_pos)))

    icd10_cancer_index = []
    for h in headers:
        if h.split('_')[1] == '40006':
            array_pos = h.split('_', 2)[2] # Grabs "0_0" from n_20004_0_0 for example
            icd10_cancer_index.append((headers.index(h), headers.index('n_40008_'+array_pos)))

    selfrep_cancer_index = []
    for h in headers:
        if h.split('_')[1] == '20001':
            array_pos = h.split('_', 2)[2] # Grabs "0_0" from n_20004_0_0 for example
            selfrep_cancer_index.append((headers.index(h), headers.index('n_20007_'+array_pos)))


    fieldnames = ['Patient_ID']
    for d in diseases:
        fieldnames.append(d)


    lines = f.readlines()


    for e, line in enumerate(lines):
        try:
            # Fix space issue in textfile. 'newline' is a patient row to be added to the output later. Patient ID is added first.
            if " " in line[:9]:
                line = line[:9].replace(" ", "\t")+line[9:]
            line = line.split('\t')
            newline = {'Patient_ID': line[0]}

            icd10_cancer_line = {line[int(i[0])] for i in icd10_cancer_index if line[int(i[0])] != ''}
            icd9_cancer_line = {line[int(i[0])] for i in icd9_cancer_index if line[int(i[0])] != ''}
            selfrep_cancer_line = {int(line[int(i[0])]) for i in selfrep_cancer_index if line[int(i[0])] != ''}

            for d in diseases:
                codes_icd10 = ast_to_codes(icd10_cancer_line, diseases[d]['ICD10'])
                codes_icd9 = ast_to_codes(icd9_cancer_line, diseases[d]['ICD9'])
                codes_selfrep = ast_to_codes(selfrep_cancer_line, diseases[d]['SELFREP_CANCER_20001'])
                newline[d] = 2000

                if (len(codes_icd10) == 0) and (len(codes_icd9) == 0) and (len(codes_selfrep) == 0):
                    newline[d] = 1000

                if len(codes_icd10) > 0:
                    icd10_cancer_tuples = {(line[int(i[0])], line[int(i[1])])  for i in icd10_cancer_index if (line[int(i[0])] != '') and (line[int(i[1])] != '')}
                    for k, v in icd10_cancer_tuples:
                        if k in codes_icd10:
                            if ((float(v) >= 0) and (v is not None) and (float(v) < newline[d])):
                                newline[d] = float(v)

                if len(codes_icd9) > 0:
                    icd9_cancer_tuples = {(line[int(i[0])], line[int(i[1])])  for i in icd9_cancer_index if (line[int(i[0])] != '') and (line[int(i[1])] != '')}
                    for k, v in icd9_cancer_tuples:
                        if k in icd9_cancer_line:
                            if ((float(v) >= 0) and (v is not None) and (float(v) < newline[d])):
                                newline[d] = float(v)

                if len(codes_selfrep) > 0:
                    selfrep_cancer_tuples = [(int(line[int(i[0])]), line[int(i[1])]) for i in selfrep_cancer_index if (line[int(i[0])] != '') and (line[int(i[1])] != '')]
                    for k, v in selfrep_cancer_tuples:
                      if k in selfrep_cancer_line:
                          if ((float(v) >= 0) and (v is not None) and (float(v) < newline[d])):
                              newline[d] = float(v)

            line_list.append(newline)
            if e%25000 == 0:
                print e

        except:
            break


with open('Age_Cancer_Disease_Apr20.csv', 'w') as c_file:
    c_writer = csv.DictWriter(c_file, fieldnames=fieldnames)
    c_writer.writeheader()
    c_writer.writerows(line_list)

# Open our file
ukb_file = pd.read_csv('Age_Cancer_Disease_Apr20.csv')

print "Translated HES File. All Files Loaded"

all_patients = {}

with open('hes_main_sec_apr_1997.csv') as f:
    header = f.readline()
    headers = header.rstrip('\n').split(',')

    # Gets the indexes for each code-type used for definitions
    icd10_index = []
    for h in headers:
        if 'diag_icd10' in h:
            icd10_index.append(headers.index(h))

    opcs_index = []
    for h in headers:
        if 'oper4' in h:
            opcs_index.append(headers.index(h))

    icd9_index = []
    for h in headers:
        if 'diag_icd9' in h:
            icd9_index.append(headers.index(h))

    icd_year_index = headers.index('icd_years')
    opcs_year_index = headers.index('opcs_years')
    patient_id = headers.index('Patient_ID')

    fieldnames = ['Patient_ID']
    for d in diseases:
        fieldnames.append(d)

    lines = f.readlines()

    for e, line in enumerate(lines):
        try:
            line = line.rstrip('\n').split(',')

            icd10_line = {line[int(i)] for i in icd10_index if line[int(i)] != ''}
            icd9_line = {line[int(i)] for i in icd9_index if line[int(i)] != ''}
            opcs_line = {line[int(i)] for i in opcs_index if line[int(i)] != ''}
            icd_year = line[icd_year_index]
            opcs_year = line[opcs_year_index]
            pid = line[patient_id]


            if pid not in all_patients:
                all_patients[pid] = {d: None for d in diseases}

            for d in diseases:
                icd_codes = len(ast_to_codes(icd10_line, diseases[d]['ICD10'])) +  len(ast_to_codes(icd9_line, diseases[d]['ICD9']))
                #oper_codes = len(ast_to_codes(opcs_line, diseases[d]['OPCS']))
                if icd_codes > 0:
                    min_age = icd_year
                    #if oper_codes > 0:
                        #if icd_year < 0:
                            #min_age = opcs_year
                        #elif opcs_year < 0:
                            #min_age = icd_year
                            #min_age = min(icd_year, opcs_year)
                #elif oper_codes > 0:
                    #min_age = opcs_year
                else:
                    min_age = None

                if min_age >= 0:
                    if all_patients[pid][d] is None:
                        all_patients[pid][d] = min_age
                    elif min_age is not None:
                        all_patients[pid][d] = min(min_age, all_patients[pid][d])

            if e%25000 == 0:
                print e
                
        except:
            break


print "Creating disease DataFrame"

age_disease_df = pd.DataFrame.from_dict(all_patients, orient='index')
age_disease_df.index.names = ['Patient_ID']
age_disease_df = age_disease_df.reset_index()
age_disease_df['Patient_ID'] = age_disease_df['Patient_ID'].astype(int)
for d in diseases:
    age_disease_df[d] = age_disease_df[d].astype(float)
    print age_disease_df[d].dtype

ukb_file2 = pd.merge(ukb_file, age_disease_df, on='Patient_ID', how='left', suffixes=('_x', '_y'))

print "Loaded UKB File. Merging diseases ages..."

for d in diseases:
    print d
    ukb_file2[d] = ukb_file2.apply(lambda row: min(age for age in (row[d+'_x'], row[d+'_y']) if str(age) != 'nan' ), axis=1)
    ukb_file2.drop([d+'_x', d+'_y'], axis=1, inplace=True)

ukb_file2.to_csv("Age_Cancer_Disease_Apr20.csv")
