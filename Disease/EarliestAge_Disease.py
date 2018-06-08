import csv
import pandas as pd
import main_func as opf
import config


reader = pd.ExcelFile(config.codes_sheet)
sheets = reader.sheet_names

diseases = {}  # Dictionary of diseases

sheets = ['STROKE', 'PREV_CAD', 'INC_ACS', 'ALL_STROKE', 'ISC_STROKE', 'HEM_STROKE', 'HF', 'AFIB', 'T1D', 'T2D', 'HYPERLIPIDEMIA', 'HYPERTENSION']

# Iterates through sheets in excel and converts them into dictionaries to access later.
for s in sheets:
    c_df = reader.parse(s, converters={'ICD9': str, 'SELFREP_MC_20002': str, 'SELFREP_OP_20004': str})

    diseases[s] = {
            'ICD10': c_df['ICD10'].dropna().unique(),
            'OPCS': c_df['OPCS'].dropna().unique(),
            'ICD9': c_df['ICD9'].dropna().unique(),
            'SELFREP_MC_20002': c_df['SELFREP_MC_20002'].dropna().unique(),
            'SELFREP_OP_20004': c_df['SELFREP_OP_20004'].dropna().unique()
            }
    for k in diseases[s]:
        diseases[s][k] = [c.replace('*', '') for c in diseases[s][k]]

"""
# (DO-NOT-CHANGE
f = open(config.ukb_file)
header = f.readline()
headers = header.split('\t')
headers[0] = '0_0'

line_list = []
lines = f.readlines()
f.close()
# DO-NOT-CHANGE)


# Must Specify Field Numbers of Fields of Interest
icd10_index = opf.get_header_indices(headers, '41202') + opf.get_header_indices(headers, '41204')
opcs_index = opf.get_header_indices(headers, '41200') + opf.get_header_indices(headers, '41210')
icd9_index = opf.get_header_indices(headers, '41203') + opf.get_header_indices(headers, '41205')
selfrep_mc_index = opf.get_header_indices(headers, '20002', '20009')
selfrep_op_index = opf.get_header_indices(headers, '20004', '20011')

# Write the column names for the output file
fieldnames = ['Patient_ID']
for d in diseases:
    fieldnames.append(d)


# 'e' is for displaying how many patient rows we have processed
for e, line in enumerate(lines):

    line = line.split('\t') # We get a list of values after tab-separating the row.

    # Writes the Patient ID to a new line in the file. If there are no more non-blank lines in the file, continue to the next portion
    newline = {'Patient_ID': line[0]}
    if newline['Patient_ID'].isspace() or len(newline['Patient_ID']) == 0:
        break

    icd10_line = opf.get_patient_vals(line, icd10_index)
    icd9_line = opf.get_patient_vals(line, icd9_index)
    opcs_line = opf.get_patient_vals(line, opcs_index)
    selfrep_mc_line = opf.get_patient_vals(line, selfrep_mc_index)
    selfrep_op_line = opf.get_patient_vals(line, selfrep_op_index)

    # patient_codes = [(code, age), (code2, age2), ...] ~ codes with their corresponding ages
    selfrep_mc_codes_and_ages = opf.get_patient_vals(line, selfrep_mc_index, return_both=True)
    selfrep_op_codes_and_ages = opf.get_patient_vals(line, selfrep_op_index, return_both=True)

    for d in diseases:

        # Returns self-reported patient codes matching disease
        selfrep_mc_disease_codes = opf.match_codes(diseases[d]['SELFREP_MC_20002'], selfrep_mc_line)
        selfrep_op_disease_codes = opf.match_codes(diseases[d]['SELFREP_OP_20004'], selfrep_op_line)

        # Returns ICD or OPCS codes matching disease
        icd10_disease_codes = opf.match_codes(diseases[d]['ICD10'], icd10_line)
        icd9_disease_codes = opf.match_codes(diseases[d]['ICD9'], icd9_line)
        opcs_disease_codes = opf.match_codes(diseases[d]['OPCS'], opcs_line)

        # If there is at least one code for this disease, the age is set to 2000. Otherwise, it is set to 1000.
        if len(icd10_disease_codes) + len(icd9_disease_codes) + len(opcs_disease_codes) + len(selfrep_mc_disease_codes) + len(selfrep_op_disease_codes) > 0:
            newline[d] = 2000
        else:
            newline[d] = 1000

        # Gets the minimum self-reported ages if a self-reported code exists
        if len(selfrep_mc_disease_codes) > 0:
            mc_min_age = opf.get_min_age(selfrep_mc_codes_and_ages, diseases[d]['SELFREP_MC_20002'])[0]
            newline[d] = min(newline[d], mc_min_age)


        if len(selfrep_op_disease_codes) > 0:
            op_min_age = opf.get_min_age(selfrep_op_codes_and_ages, diseases[d]['SELFREP_OP_20004'])[0]
            newline[d] = min(newline[d], op_min_age)


    line_list.append(newline)
    if e%25000 == 0:
        print e


with open('Disease_Ages_prehes.csv', 'w') as c_file:
    c_writer = csv.DictWriter(c_file, fieldnames=fieldnames)
    c_writer.writeheader()
    c_writer.writerows(line_list)
"""
# ------------------------------- HES ----------------------------------


def process_file(headers, output_column_names):
    """You may modify this function"""
    # Gets the indexes for each code-type used for definitions
    field_index = {}
    groupby_dict = {}

    field_index['ICD10'] = opf.get_header_indices(headers, 'diag_icd10')
    field_index['ICD9'] = opf.get_header_indices(headers, 'diag_icd9')
    field_index['OPCS'] = opf.get_header_indices(headers, 'oper4')
    field_index['ICD_YEAR'] = opf.get_header_indices(headers, 'icd_years')[0]
    field_index['OPCS_YEAR'] = opf.get_header_indices(headers, 'opcs_years')[0]
    field_index['Patient_ID'] = opf.get_header_indices(headers, 'Patient_ID')

    for d in diseases:
        output_column_names.append(d)
        groupby_dict[d] = 'min'

    return field_index, output_column_names, groupby_dict


def next_row(line, output_row, output_column_names, field_index):
    """You may modify this function."""

    # Get Age for each admission. Make sure to convert to float
    # Can also do float(opf.get_patient_vals(line, icd_year_index)[0]) to get the first value


    icd_year = float(line[field_index['ICD_YEAR']])
    opcs_year = float(line[field_index['OPCS_YEAR']])

    # Get patient values for each type of code
    icd10_line = opf.get_patient_vals(line, field_index['ICD10'])
    icd9_line = opf.get_patient_vals(line, field_index['ICD9'])
    opcs_line = opf.get_patient_vals(line, field_index['OPCS'])

    for d in diseases:

        output_row[d] = 2000  # Defaults min_age to 2000

        # Returns ICD or OPCS codes matching disease
        icd10_disease_codes = opf.match_codes(diseases[d]['ICD10'], icd10_line)
        icd9_disease_codes = opf.match_codes(diseases[d]['ICD9'], icd9_line)
        opcs_disease_codes = opf.match_codes(diseases[d]['OPCS'], opcs_line)

        # Gets the minimum age if codes are present
        if len(icd10_disease_codes) + len(icd9_disease_codes) > 0:
            output_row[d] = min(output_row[d], icd_year)
        if len(opcs_disease_codes) > 0:
            output_row[d] = min(output_row[d], opcs_year)

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

    hes_file = pd.DataFrame(row_list, columns=row_list[0].keys())

    for d in groupby_dict:
        if d == 'concat':
            groupby_dict[d] = lambda x: '%s'%','.join(x)

    grouped_patients = hes_file.groupby(merge_id).agg(groupby_dict).reset_index()

    return grouped_patients


def merge_ukb_hes(ukb_file, age_disease_df, overlap_columns):

    print "Loaded UKB File. Merging diseases ages..."
    # Merge Main File Output and HES File Output
    merged_file = pd.merge(ukb_file, age_disease_df, on='Patient_ID', suffixes=('_x', '_y'))
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

    # Open our output file from main UKB
    ukb_file = pd.read_csv('Disease_Ages_prehes.csv')

    output_column_names = ['Patient_ID']
    print 'There are ' + str(len(patient_rows))+ ' rows in the HES file. The program will output the total number of lines processed below: '

    field_index, output_column_names, groupby_dict = process_file(headers, output_column_names)
    output_rows = iterate_rows(patient_rows, output_rows, output_column_names, field_index)

    print output_rows[:5]

    output_rows = group_all_patients(output_rows, groupby_dict, 'Patient_ID')

    print output_rows.head()

    print "Creating Disease DataFrame"

    #age_disease_df = pd.DataFrame.from_dict(output_rows, orient='index')
    output_rows.index.names = ['Patient_ID']
    #output_rows = output_rows.reset_index()
    output_rows['Patient_ID'] = output_rows['Patient_ID'].astype(int)

    merged_file = merge_ukb_hes(ukb_file, output_rows, diseases)

    merged_file.to_csv("Disease_Ages.csv")

hes_main()
