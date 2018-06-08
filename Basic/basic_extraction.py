import csv
import pandas as pd
import config
import sheets as sh
import main_func as opf

# Your Variables
icd10_codes_you_want = ['E66', 'E78', 'E87']

def process_file(headers, output_column_names):
    """You may modify this function."""

    # Must Specify Field Numbers of Fields of Interest
    field_index = {}

    field_index['ICD10'] = opf.get_header_indices(headers, '41202') + opf.get_header_indices(headers, '41204')

    # I want each code to be a column name
    for code in icd10_codes_you_want:
        output_column_names.append(code)

    return field_index, output_column_names


def next_row(line, output_row, output_column_names, field_index):
    """You may modify this function."""

    icd10_patient_values = opf.get_patient_vals(line, field_index['ICD10'])

    for code in icd10_codes_you_want:
        matching_values = opf.match_codes([code], icd10_patient_values)

        output_row[code] = 0
        if len(matching_values) > 0:
            output_row[code] = 1

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
