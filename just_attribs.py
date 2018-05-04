import sys
import csv
import pandas as pd
import numpy as np
import time

line_list = []

reader = pd.ExcelFile("attribs.xlsx")
sheets = reader.sheet_names

# Iterates through sheets in excel and converts them into dictionaries to access later.
for s in sheets:
    if s == 'ATTRIBUTES':
        c_df = reader.parse(s)
        attrib = dict(zip(c_df.Attribute, c_df.Code))
        attrib_input = dict(zip(c_df.Attribute, c_df.Input))
        attrib_conversion = {}
        for i, row in c_df.iterrows():
            # For each attribute in the attributes, if the 'Conversion' cell is not empty
            if str(row['Binary']) != 'nan':

                # The input is AI and the conversion is not a dictionary, but a list
                if (str(row['Input']).strip() == 'AI'):
                    # Create a list from the comma-separated conversion cell
                    attrib_conversion[row['Attribute']] = set(str(row['Binary']).replace(' ', '').split(','))

                # The input is EITHER blank, 'F', or 'AS'
                elif (str(row['Input']).strip() != 'AI'):
                    # Creates a dictionary from the values in 'Conversion'
                    attrib_conversion[row['Attribute']] = {}
                    for item in row['Binary'].replace(' ', '').split(';'):
                        k, v = item.split(':')
                        v_list = v.split(',')
                        attrib_conversion[row['Attribute']][k] = v_list
                else:
                    print "ERROR"
                    break

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
                    attrib_index[a] = [headers.index(h)]
        elif underscore_count == 1:  # Entire Array for Specific Instance

            # If Input is NOT empty, create ONE fieldname with just the attribute name and get a list of all indexes associated with that specific array of the fieldname.
            if str(attrib_input[a]) != 'nan':
                attrib_index[a] = []
                for h in headers:
                    if str(attrib[a]) == h.split('_', 1)[1].rsplit('_', 1)[0]:
                        attrib_index[a].append(headers.index(h))

            # If the input IS empty, create SEVERAL fieldnames for each index in that specific array.
            else:
                for h in headers:
                    if str(attrib[a]) == h.split('_', 1)[1].rsplit('_', 1)[0]:
                        attrib_index[a+'_'+h.split('_')[-1]] = [headers.index(h)]

        elif underscore_count == 0:  # Entire Array for All Instances

            # If Input is F, create ONE fieldname with just the attribute name and get a list of all indexes associated with that fieldname.
            if str(attrib_input[a]) == 'F':
                attrib_index[a] = []
                for h in headers:
                    if str(attrib[a]) == h.split('_')[1]:
                        attrib_index[a].append(headers.index(h))
            # If Input is AI, create a dictionary of instances with a list of indexes for the array positions
            elif str(attrib_input[a]) == 'AI':
                attrib_arrays = {}
                for instance in ('0', '1', '2'):
                    attrib_arrays[a+'_'+instance] = []
                    for h in headers:
                        if str(attrib[a])+'_'+instance == h.split('_', 1)[1].rsplit('_', 1)[0]:
                            attrib_arrays[a+'_'+instance].append(headers.index(h))
                attrib_index[a] = attrib_arrays
            else:
                for h in headers:
                    if str(attrib[a]) == h.split('_')[1]:
                        attrib_index[a+'_'+h.split('_', 2)[-1]] = [headers.index(h)]


    fieldnames = ['Patient_ID']
    for a in attrib_index:
        fieldnames.append(a)

    lines = f.readlines()

    for e, line in enumerate(lines):
        try:
            # Fix space issue in textfile. 'newline' is a patient row to be added to the output later. Patient ID is added first.
            if " " in line[:9]:
                line = line[:9].replace(" ", "\t")+line[9:]
            line = line.split('\t')
            newline = {'Patient_ID': line[0]}

            for a in attrib_index:
                if ((a in attrib_input) and (attrib_input[a] == 'AI')):
                    # Only iterates through dictionaries of arrays (0, 1, 2). Need to change for 'A' input on single arrays
                    for inst_num in xrange(3):
                        # Gets non-blank patient values for specific array of attribute
                        arr = a+'_'+str(inst_num)
                        attrib_arr = {line[int(item)] for item in attrib_index[a][arr] if line[int(item)] != ''}
                        # If the do not have values, go to the next array
                        if len(attrib_arr) > 0:
                            if len(attrib_arr&attrib_conversion[a]) > 0:
                                newline[a] = 1
                            else:
                                newline[a] = 0
                else:
                    # Get the first value that is not blank. If all values are blank, return a blank.
                    attrib_0 = next((line[int(item)] for item in sorted(attrib_index[a]) if str(line[int(item)]) != 'nan'), '')

                    # Gets the attribute name in the conversion dictionary that is associated with the current attribute. The current attribute may be called fieldname or fieldname_0_0. Checks for a partial name match (b in a).
                    get_b = [b for b in attrib_conversion.keys() if str(b) in str(a)]

                    # If the attribute has a conversion value, sets the current attribute to the first non-blank value...
                    if len(get_b) > 0:
                        newline[a] = attrib_0
                        for k, v in attrib_conversion[get_b[0]].items():
                            # Converts the current value if it exists in conversion dict for attribute
                            if str(attrib_0) in v:
                                newline[a] = k
                                break
                    elif attrib_0 == '':
                        newline[a] = None
                    else:
                        newline[a] = attrib_0

            line_list.append(newline)
            if e%25000 == 0:
                print e
        except:
            break



with open('attrib_pull.csv', 'w') as c_file:
    c_writer = csv.DictWriter(c_file, fieldnames=fieldnames)
    c_writer.writeheader()
    c_writer.writerows(line_list)
