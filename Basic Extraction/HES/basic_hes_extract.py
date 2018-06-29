# HES Processing Script

import csv
import pandas as pd
import main_func as opf
import config

# Partial Matches on These Codes
afib_icd10_codes = ['I48']
afib_icd9_codes = ['4273']

# You may want to list the malformations that the patient has,
icd10_mapping = {
'I350': 'AORTIC_STENOSIS_COND',
'I351': 'AORTIC_INSUFFICIENCY_COND',
'I352': 'AORTIC_INSUFFICIENCY_COND'}

# If only concerned with patients that were diagnosed PRIOR to a certain age, you can create a dictionary for that to check ages later.
code_age_mapping = {'AORTIC_STENOSIS_COND': 60, 'AORTIC_INSUFFICIENCY_COND': 60}


def process_file(headers):
    """You may modify this function"""
    # Gets the indexes for each code-type used for definitions. Do not modify
    field_index = {}
    groupby_dict = {}

    field_index['ICD10'] = opf.get_header_indices(headers, 'diag_icd10')
    field_index['ICD9'] = opf.get_header_indices(headers, 'diag_icd9')
    field_index['ICD_YEAR'] = opf.get_header_indices(headers, 'icd_years')
    field_index['Patient_ID'] = opf.get_header_indices(headers, 'Patient_ID')


    groupby_dict['AFIB_Codes'] = 'concat'
    groupby_dict['Earliest_Afib_Diagnosis'] = 'min'
    groupby_dict['Other_Malformations'] = 'concat'
    groupby_dict['Minimum_Age_At_Other_Malformations'] = 'min'

    return field_index, groupby_dict


def next_row(line, output_row, output_column_names, field_index):
    """You may modify this function."""

    # Get Age for each admission. Make sure to convert to float
    # Can also do float(opf.get_patient_vals(line, icd_year_index)[0]) to get the first value

    # pop() returns the first element in a set. The function get_patient_vals always returns a set of unique values. If there are no non-blank values, it will return an empty set. Here we check if the set is empty, and assign age_at_icd_code to 2000 if there is no available age.

    age_at_icd_code = 2000
    age_list = opf.get_patient_vals(line, field_index['ICD_YEAR'])
    if len(age_list) != 0:
        age_at_icd_code = age_list.pop()

    # Get patient values for each type of code
    icd10_patient_values = opf.get_patient_vals(line, field_index['ICD10'])
    icd9_patient_values = opf.get_patient_vals(line, field_index['ICD9'])

    # Find AFIB Codes and get the ages at which the patients were diagnosed ----
    output_row['AFIB_Codes'] = ','.join(opf.match_codes(afib_icd10_codes, icd10_patient_values) + opf.match_codes(afib_icd9_codes, icd9_patient_values))

    if len(output_row['AFIB_Codes']) > 0:
        output_row['Earliest_Afib_Diagnosis'] = age_at_icd_code
    else:
        output_row['Earliest_Afib_Diagnosis'] = 2000
    # --------------------------------------------------------------------------

    # Find 'Other' Codes and Translate to Malformations. Only include malformations that meet age criteria and return age if it meets criteria ----------------------------------------
    other_icd10_mals = opf.match_codes(icd10_mapping, icd10_patient_values)
    output_row['Other_Malformations'] = []

    for malformation in other_icd10_mals:
        if float(age_at_icd_code) < code_age_mapping[malformation]:
            output_row['Other_Malformations'].append(malformation)

    output_row['Other_Malformations'] = ','.join(output_row['Other_Malformations'])

    if len(output_row['Other_Malformations']) > 0:
        output_row['Minimum_Age_At_Other_Malformations'] = age_at_icd_code
    else:
        output_row['Minimum_Age_At_Other_Malformations'] = 2000
    # --------------------------------------------------------------------------

    return output_row


def iterate_rows(patient_rows, output_rows, output_column_names, field_index):
    """ DO NOT modify this function. """
    for e, line in enumerate(patient_rows):
        line = line.rstrip('\n').split(',') # We get a list of values after comma-separating the row.

        output_row = {'Patient_ID': line[field_index['Patient_ID'][0]]}
        if output_row['Patient_ID'].isspace() or len(output_row['Patient_ID']) == 0:
            break

        output_row = next_row(line, output_row, output_column_names, field_index)
        output_rows.append(output_row)

        if e%25000 == 0:
            print e

    return output_rows


def group_all_patients(row_list, groupby_dict, merge_id):
    """ Do not modify this function. Groups all the values in the HES file according to some criteria specified in the 'process_file' function"""
    hes_file = pd.DataFrame(row_list, columns=row_list[0].keys())

    new_group_dict = {}
    for d in groupby_dict:
        if groupby_dict[d] == 'concat':
            new_group_dict[d] = lambda x: '%s'%','.join(x)
        else:
            new_group_dict[d] = groupby_dict[d]

    print 'Grouping File'

    grouped_patients = hes_file.groupby(merge_id).agg(new_group_dict).reset_index()

    for d in groupby_dict:
        if groupby_dict[d] == 'concat':
            grouped_patients[d] = grouped_patients[d].apply(lambda vals: ','.join({x for x in vals.split(',') if len(x) > 0}))

    return grouped_patients


def merge_ukb_hes(ukb_file, hes_df, overlap_columns):

    print "Loaded UKB File. Merging HES File..."
    # Merge Main File Output and HES File Output
    merged_file = pd.merge(ukb_file, hes_df, how='left', on='Patient_ID', suffixes=('_x', '_y'))
    # Get the minimum disease ages between self-reported data and HES file.
    for d in overlap_columns:
        print d
        merged_file[d] = merged_file.apply(lambda row: min(age for age in (row[d+'_x'], row[d+'_y']) if str(age) != 'nan' ), axis=1)
        merged_file.drop([d+'_x', d+'_y'], axis=1, inplace=True)  # Drop irrelevant columns

    return merged_file


def hes_main():

    # (DO-NOT-CHANGE
    f = open(config.hes_file)
    header = f.readline()
    headers = header.rstrip('\n').split(',')
    headers = ['n_'+h for h in headers]

    output_rows = []
    patient_rows = f.readlines()
    f.close()
    # DO-NOT-CHANGE)

    output_column_names = ['Patient_ID']
    print 'There are ' + str(len(patient_rows))+ ' rows in the HES file. The program will output the total number of lines processed below: '

    field_index, groupby_dict = process_file(headers)

    for key in groupby_dict:
        output_column_names.append(key)

    output_rows = iterate_rows(patient_rows, output_rows, output_column_names, field_index)

    print output_rows[:5]

    output_rows = group_all_patients(output_rows, groupby_dict, 'Patient_ID')

    print output_rows[:5]

    print "Creating DataFrame"

    #age_disease_df = pd.DataFrame.from_dict(output_rows, orient='index')
    output_rows.index.names = ['Patient_ID']
    #output_rows = output_rows.reset_index()
    output_rows['Patient_ID'] = output_rows['Patient_ID'].astype(int)

    output_rows.to_csv(config.output_filename)

hes_main()
