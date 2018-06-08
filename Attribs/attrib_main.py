
import pandas as pd
import sheets as sh
import config
import ast
import op_functions as opf
import attrib_func as af

line_list = []

reader = pd.ExcelFile(config.codes_sheet)
sheets = reader.sheet_names

# Finds the attributes sheet
s = sheets.index('ATTRIBUTES')

# Creates 3 separate dictionaries:
    # the field code
    # the select value (how many values will be selected)
    # the conversion dictionary
attrib = sh.sheet_to_dict(reader, s, 'Attribute', 'Code')
attrib_select = sh.sheet_to_dict(reader, s, 'Attribute', 'Input')
attrib_conversion = sh.sheet_to_dict(reader, s, 'Attribute', 'Binary')


with open(config.ukb_file) as f:
    header = f.readline()
    headers = header.split('\t')
    headers[0] = '0_0'

    attrib_index = {}

    # We find the indicies of the attributes we are interested in.
    for a in attrib:

        if attrib_select[a] in ('F', 'A'): # There will only be one column associated with this attribute
            attrib_index[a] = opf.get_header_indices(headers, attrib[a])

        else: # Output all values into separate columns
            all_indices = opf.get_header_indices(headers, attrib[a])

            if len(all_indices) > 1:
                column_num = 0
                for index in all_indices:
                    new_column = a + '_' + str(column_num) # Format: Attribute_0, Attribute_1, etc.
                    attrib_index[new_column] = [index]
                    attrib_select[new_column] = attrib_select[a]
                    attrib_conversion[new_column] = attrib_conversion[a]
                    column_num += 1
            else:
                attrib_index[a] = all_indices


    # Write columns for output file
    fieldnames = ['Patient_ID']
    for a in attrib_index:
        fieldnames.append(a)

    lines = f.readlines()

    for e, line in enumerate(lines):
        # Fix space issue in textfile. 'newline' is a patient row to be added to the output later. Patient ID is added first.
        if " " in line[:9]:
            line = line[:9].replace(" ", "\t")+line[9:]
        line = line.split('\t')

        newline = {'Patient_ID': line[0]}
        if newline['Patient_ID'].isspace() or len(newline['Patient_ID']) == 0:
            break

        for a in attrib_index:
            attrib_values = opf.get_patient_vals(line, attrib_index[a])

            default_value = None
            if a == 'Qualifications (college)':
                default_value = 'NoCollege'
            if a in ('Paternal_CVD', 'Maternal_CVD'):
                default_value = 0

            newline[a] = af.single_output_conversion(list_of_values=attrib_values, convert_dict=attrib_conversion[a], default_value=default_value, input_value=attrib_select[a])


        line_list.append(newline)

        if e%25000 == 0:
            print e



attrib_df = pd.DataFrame(line_list, columns=fieldnames)
#attrib_df.to_csv('attrib_pull_main.csv')
