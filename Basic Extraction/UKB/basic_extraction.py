import csv
import pandas as pd
import config
import main_func as opf
import sys

# Your Possible Variables
single_icd10_codes_of_interest = ['E66', 'E78', 'E87']

stroke_codes = {
'ICD9': ['433', '434', '435', '436'],
'ICD10': ['I63', 'G45', 'I64', 'G46'],
'SelfRep_MC': ['1583', '1081', '1082']}

# You may want to list the malformations that the patient has,
selfreported_med_codes = {
'1490': 'AORTIC_STENOSIS_COND',
'1586': 'AORTIC_VALVE_UNSPECIFIED_COND',
'1587': 'AORTIC_INSUFFICIENCY_COND'}

# If only concerned with patients that were diagnosed PRIOR to a certain age, you can create a dictionary for that to check ages later.
selfreported_code_age_mapping = {'1490': 60, '1586': 60, '1587': 60}


def process_file(headers, output_column_names):
    """This function is used to find and specify which fields in Biobank you are interested in and what columns you want in your output file. You may modify this function."""

    # Must Specify Field Numbers of Fields of Interest. Do Not Change
    field_index = {}

    # This tells the program where the codes are in the file
    field_index['ICD10'] = opf.get_header_indices(headers, '41202') + opf.get_header_indices(headers, '41204')
    field_index['ICD9'] = opf.get_header_indices(headers, '41203') + opf.get_header_indices(headers, '41205')
    field_index['SelfRep_MC'] = opf.get_header_indices(headers, '20002', '20009')

    field_index['Year_Of_Birth'] = opf.get_header_indices(headers, '34')

    output_column_names.append('Year_Of_Birth')

    # I want each code to be a column name
    for code in single_icd10_codes_of_interest:
        output_column_names.append(code)

    # I want 'Stroke' to be an output column
    output_column_names.append('Stroke')

    # I want to know what self-reported medical malformations the patient has and the minimum age at which the patient was diagnosed. So I'll have two self-reported columns. Patients will only be assigned a malformation if they meet age criteria.
    output_column_names.append('SelfReported_Malformations')
    output_column_names.append('Minimum_Age_At_SelfReported_Malformation')

    return field_index, output_column_names


def next_row(line, output_row, output_column_names, field_index):
    """This function lets you handle each row in the biobank file one at a time. Expects a dictionary of values that will become one line of output in your output file. All biobank values will be of type 'string', make sure to convert to float or int when comparing numerical values but not codes that may start with 0 (e.g. - ICD9). You may modify this function."""

    # This will output all of the patient's codes
    icd10_patient_values = opf.get_patient_vals(line, field_index['ICD10'])
    icd9_patient_values = opf.get_patient_vals(line, field_index['ICD9'])
    selfrep_mc_patient_values = opf.get_patient_vals(line, field_index['SelfRep_MC'])
    selfrep_mc_patient_values_with_ages = opf.get_patient_vals(line, field_index['SelfRep_MC'], return_both=True)

    output_row['Year_Of_Birth'] = [c for c in opf.get_patient_vals(line, field_index['Year_Of_Birth'])][0]

    # -------------------------------------------------------------------------------

    for code in single_icd10_codes_of_interest:
        matching_values = opf.match_codes([code], icd10_patient_values)

        output_row[code] = 0
        if len(matching_values) > 0:
            output_row[code] = 1

    # -------------------------------------------------------------------------------

    # Find Matching Stroke Codes
    stroke_values = opf.match_codes(stroke_codes['ICD9'], icd9_patient_values) + opf.match_codes(stroke_codes['ICD10'], icd10_patient_values) + opf.match_codes(stroke_codes['SelfRep_MC'], selfrep_mc_patient_values)

    output_row['Stroke'] = 0
    if len(stroke_values) > 0:
        output_row['Stroke'] = 1

    # -------------------------------------------------------------------------------

    selfrep_mc_min_age, selfrep_mc_codes_with_age_met = opf.get_min_age(selfrep_mc_patient_values_with_ages, selfreported_med_codes, age_criteria_dict = selfreported_code_age_mapping)

    output_row['Minimum_Age_At_SelfReported_Malformation'] = selfrep_mc_min_age

    # To Translate the self-reported codes to malformations, you can do the following or translate them yourself. The 'join' function turns the list into a comma-separated string of malformations.
    output_row['SelfReported_Malformations'] = ','.join(opf.match_codes(selfreported_med_codes, selfrep_mc_codes_with_age_met))

    """
    # We'll show you what the above output looks like without translation for a patient that has the codes. The program will exit after printing. It may have to process a few lines before printing. This is just for understanding the program, you can remove the following.
    if len(selfrep_mc_codes_with_age_met) > 1:

        print '\n----------------------------'
        print 'SelfReported Medical Codes:'
        print selfrep_mc_codes_with_age_met
        print '\n'
        print 'Self-Reported Medical Malformations:'
        print opf.match_codes(selfreported_med_codes, selfrep_mc_codes_with_age_met)
        print '\n'
        print 'Self-Reported Medical Malformations as Comma-Separated String:'
        print output_row['SelfReported_Malformations']
        print '\n'
        print 'Minimum Age For Self-Reported Codes:'
        print output_row['Minimum_Age_At_SelfReported_Malformation']
        print '----------------------------'

        sys.exit()
    """

    return output_row


def iterate_rows(patient_rows, output_rows, output_column_names, field_index):
    """ DO NOT modify this function. """
    for e, line in enumerate(patient_rows):
        line = line.split('\t') # We get a list of values after tab-separating the
        output_row = {'Patient_ID': line[0]}
        if output_row['Patient_ID'].isspace() or len(output_row['Patient_ID']) == 0:
            break

        output_row = next_row(line, output_row, output_column_names, field_index)
        output_rows.append(output_row)

        if e%25000 == 0:
            print e

    return output_rows


def main():
    """ DO NOT modify this function """
    f = open(config.ukb_file)
    header = f.readline()
    headers = header.split('\t')
    headers[0] = '0_0'

    output_rows = []
    patient_rows = f.readlines()
    f.close()

    output_column_names = ['Patient_ID']
    print 'There are ' + str(len(patient_rows))+ ' rows in the UKB file. The program will output the total number of lines processed below: '

    field_index, output_column_names = process_file(headers, output_column_names)

    if (type(field_index) == dict) and (type(output_column_names) == list):

        output_rows = iterate_rows(patient_rows, output_rows, output_column_names, field_index)

        with open(config.output_filename, 'w') as c_file:
            c_writer = csv.DictWriter(c_file, fieldnames=output_column_names)
            c_writer.writeheader()
            c_writer.writerows(output_rows)
    else:
        print "ERROR from process_file function. Variables: field_index must be type 'dict' and output_column_names must be type 'list'"

main()
