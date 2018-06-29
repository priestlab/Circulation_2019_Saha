import pandas as pd


def get_header_indices(headers, bb_field, bb_field_age=None):
    """ Returns a list of indices or a list of tuples with indices that correspond to specific fields in the file"""

    # If there is no age field, return a list of indices
    field_indices = []
    if not bb_field_age:
        for h in headers:
            field_code = h.split('_', 1)[1] # e.g. - Looks at 20002_0_0, from n_20002_0_0
            if (field_code.startswith(str(bb_field)+'_')) or (field_code == str(bb_field)):
                field_indices.append(headers.index(h))
    else:
        for h in headers:
            if h.split('_')[1] == str(bb_field_age):
                age_string  = h.rsplit('_', 2)[0]   # e.g. - age_string = n_20009, from n_20009_0_0
                break

        # Returns a tuple of the (field index, age index), where age index corresponds to the exact field index.
        # e.g. - The ICD10 code 'I881' exists at n_20002_0_0
        #        The age '31' exists at n_20009_0_0.
        #        The ages for 20009 correspond to the field 20002.

        for h in headers:
            if h.split('_')[1] == str(bb_field):
                array_pos = '_'+h.split('_', 2)[2] # e.g.- array_pos = "_0_0" from n_20002_0_0
                field_indices.append((headers.index(h), headers.index(age_string+array_pos)))

    return field_indices


def get_patient_vals(line, index_list, return_both = False):
    """Returns patient values that correspond to the given indices"""

    if len(index_list) == 0:
        return {}

    if type(index_list[0]) == tuple:
        if return_both:
            return {(line[int(i[0])], line[int(i[1])]) for i in index_list
            if (line[int(i[0])] != '') and (line[int(i[1])] != '')}
        else:
            return {(line[int(i[0])]) for i in index_list if line[int(i[0])] != ''}
    else:
        return {line[int(i)] for i in index_list if line[int(i)] != ''}


def ends_with(values, partial_string, all_vals=True):
    """Returns a boolean (True/False) if values end with the partial string."""
    if all_vals and (len(values) > 0):
        return all(v.endswith(partial_string) for v in values)
    else:
        return any(v.endswith(partial_string) for v in values)


def coexist(tuple_list, main_values, conditional_values, return_existing_cond = False):
    """ Say you have a list of tuples. Each tuple contains two values which may co-exist. This function returns the values that coexist based on the values the patient has"""

    existing_main_values = []
    existing_conditional_values = []
    for tup in tuple_list:
        if (tup[0] in main_values) and (tup[1] in conditional_values):
            existing_main_values.append(tup[0])
            existing_conditional_values.append(tup[1])
    if return_existing_cond:
        return set(existing_main_values), set(existing_conditional_values)
    else:
        return set(existing_main_values)


def match_codes(key_codes, patient_codes):
    """The key_codes will be partially matched to the patient_codes and return the values of those keys if key_codes is a dictionary. Otherwise it will return the matching codes. A partial match means: “E50” can match patient values “E500”, “E501”, and “E50” for example"""

    # Ensure no null values in key_codes and patient_codes
    if type(key_codes) == dict:
        key_codes = {str(k):str(key_codes[k]) for k in key_codes.keys() if str(k) != 'nan' and str(key_codes[k]) != 'nan'}
    else:
        key_codes = [str(c) for c in key_codes if str(c) != 'nan']

    patient_codes = [str(c) for c in patient_codes if str(c) != 'nan']

    # Return empty list if there are no codes
    if len(key_codes) == 0:
        return []

    # List of codes we will be comparing our patient values to
    code_list = key_codes
    if type(key_codes) == dict:
        code_list = key_codes.keys()

    matched_codes = []

    # Partially matches codes that have an asterisk at the end. Exact matches for codes without an asterisk

    for p in patient_codes:
        matched_codes.extend([c for c in code_list if p.startswith(c)])

    if type(key_codes) == dict:
        return [key_codes[k] for k in matched_codes]
    else:
        return matched_codes


def get_min_age(patient_code_age_tuples, key_codes, age_criteria_dict = None):
    """ Returns the Minimum age and codes where the codes match the key codes"""
    min_age = 2000
    available_codes = []

    for k, v in patient_code_age_tuples:
        if k in key_codes:
            if (float(v) >= 0) and (v is not None):
                if age_criteria_dict and (k in age_criteria_dict) and (float(v) >= age_criteria_dict[k]):
                    continue
                if (float(v) < min_age):
                    min_age = float(v)
                available_codes.append(k)

    return min_age, available_codes


def single_output_conversion(list_of_values, conversion=None, default_value = None, input_value=None):
    """Converts a single value or a list of values into a different value for readability and analysis"""
    return_value = None

    if (not input_value) and len(list_of_values) == 1:
        single_value = list(list_of_values)[0]
        if conversion:
            if single_value and (default_value is not None):
                return_value = default_value
            for k in conversion:
                if single_value in conversion[k]:
                    return_value = k
            return return_value
        else:
            return single_value

    if input_value == 'F':
        next_value = next((v for v in list_of_values), None)
        if next_value == '':
            return None
        if conversion:
            if next_value and (default_value is not None):
                return_value = default_value
            for k in conversion:
                if next_value in conversion[k]:
                    return_value = k

    if input_value == 'A':
        if len(list_of_values) > 0 and (default_value is not None):
            return_value = default_value

        for k in conversion:
            if any(patient_val in conversion[k] for patient_val in list_of_values):
                return_value = k
                break


    return return_value
