import sys
import csv
import pandas as pd
import numpy as np
import time

line_list = []

reader = pd.ExcelFile("ComorbidityPhenotypes_v3.xlsx")
sheets = reader.sheet_names

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

diseases = {}

for s in sheets:

    # Prevents ICD9 codes from being read as integers.
    try:
        c_df = reader.parse(s, converters={'ICD9': str})
    except:
        c_df = reader.parse(s)
    diseases['Death_'+s] = {'ICD10': c_df['ICD10'].unique(), 'OPCS': c_df['OPCS'].unique(), 'ICD9': c_df['ICD9'].unique(), 'SELFREP_MC_20002': c_df['SELFREP_MC_20002'].unique()}

fieldnames = ['Patient_ID']
for d in diseases:
    fieldnames.append(d)

with open('app15860_standard_data_2016Nov19.txt') as f:
    header = f.readline()
    headers = header.split('\t')
    headers[0] = 'app15860_app15860'

    icd10_death_main = []
    for h in headers:
        if '40001' == h.split('_')[1]:
            icd10_death_main.append(headers.index(h))

    icd10_death_sec = []
    for h in headers:
        if '40002' == h.split('_')[1]:
            icd10_death_sec.append(headers.index(h))

    lines = f.readlines()

    for e, line in enumerate(lines):
        try:
            # Fix space issue in textfile. 'newline' is a patient row to be added to the output later. Patient ID is added first.
            if " " in line[:9]:
                line = line[:9].replace(" ", "\t")+line[9:]
            line = line.split('\t')
            pid = line[0]
            newline = {'Patient_ID': line[0]}

            primary_death = {line[int(i)] for i in icd10_death_main if line[int(i)] != ''}
            sec_death = {line[int(i)] for i in icd10_death_sec if line[int(i)] != ''}

            for d in diseases:
                # Neither the ICD10 nor the OPCS codes exist in each respective list.
                if ((len(ast_to_codes(primary_death, diseases[d]['ICD10'])) == 0) and (len(ast_to_codes(sec_death, diseases[d]['ICD10'])) == 0)):
                    newline[d] = 0
                else:
                    newline[d] = 1

            line_list.append(newline)
            if e%25000 == 0:
                print e
        except:
            break

with open('ComorbidityPhenotypes_v3_Death.csv', 'w') as c_file:
    c_writer = csv.DictWriter(c_file, fieldnames=fieldnames)
    c_writer.writeheader()
    c_writer.writerows(line_list)
