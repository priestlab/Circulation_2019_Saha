import pandas as pd


def get_header_indices(headers, field_number, age_field_number=None):
    """ Returns a list of indices or a list of tuples with indices that correspond to specific fields in the file"""

    # If there is no age field, return a list of indices
    field_indices = []
    if not age_field_number:
        for h in headers:
            field_code = h.split('_', 1)[1] # e.g. - Looks at 20002_0_0, from n_20002_0_0
            if (field_code.startswith(str(field_number)+'_')) or (field_code == str(field_number)):
                field_indices.append(headers.index(h))
    else:
        for h in headers:
            if h.split('_')[1] == str(age_field_number):
                age_string  = h.rsplit('_', 2)[0]   # e.g. - age_string = n_20009, from n_20009_0_0
                break

        # Returns a tuple of the (field index, age index), where age index corresponds to the exact field index.
        # e.g. - The ICD10 code 'I881' exists at n_20002_0_0
        #        The age '31' exists at n_20009_0_0.
        #        The ages for 20009 correspond to the field 20002.

        for h in headers:
            if h.split('_')[1] == str(field_number):
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
    """ Returns boolean if partial_string is contained at the end a value
        if all_vals is true, all values must contain the partial string,
        otherwise some values must contain the partial sring."""
    if all_vals and (len(values) > 0):
        return all(v.endswith(partial_string) for v in values)
    else:
        return any(v.endswith(partial_string) for v in values)


def has_condition(tuple_list, main_values, conditional_values, return_existing_cond = False):
    """ If two values from a tuple exist in the main values and conditional values respectively,
        return main_values where tuple exists, unless return_existing_cond = True, then return both main_values and conditional_values where tuple exists.

        e.g. - main_values = ['HEART SURGERY', 'ASD PFO']
               We do not want the following values to exist in a patient: ("HEART SURGERY", "AORTITIS")
               If HEART SURGERY exists in the patient's main values and AORTITIS exists in the patient's conditional values, HEART SURGERY is removed from main values.
               main_values = ['HEART SURGERY']    <- Function Output (return_existing_cond = False)
               conditional_values = ['AORTITIS']    <- Function Output (return_existing_cond = True)

        tuple_list (required): Accepts a list or set of tuples
        main_values (required): Accepts a list of values that may or may not match the first instance of the tuple
        conditional_values (required): Accepts a list of values that may or may not match the second instance of the tuple
        return_existing_cond (optional): If true, returns both main and conditional values where paired tuple values exist. Otherwise, returns just main_values."""

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
    """ If the key_codes is a dictionary. The patient codes will be matched to the keys and return the values of those keys. Otherwise it will return the matching codes for key_codes and patient_codes.

    e.g. - Key_Codes_Dict = {X101: 'Heart_Surgery'}
           Key_Codes_List = [X101]
           Patient_Codes = [X101, I880]

           codes_of_interest(Key_Codes_Dict, Patient_Codes)
                RETURNS: ['Heart_Surgery']

           codes_of_interest(Key_Codes_List, Patient_Codes)
                RETURNS: [X101]

    """


    # Ensure no null values in key_codes and patient_codes
    if type(key_codes) == dict:
        key_codes = {str(k):str(key_codes[k]) for k in key_codes.keys() if str(k) != 'nan' and str(key_codes[k]) != 'nan'}
    elif type(key_codes) == list:
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
    """ Returns the Minimum age and codes where the codes match the key codes. If there is an age criteria, returns an age that is LESS than those in age_criteria_dict.
        - patient_code_age_tuples: [(code1, age1), (code1, age2), (code2, age3)...]
        - key_codes: [code1, code3, ...]
        - age_criteria_dict: {code1: age_criteria_1, code3: age_criteria2}
        # Returns the minimum of age1 and age2, IF they're less than age_criteria_1
    """
    min_age = 2000
    available_codes = []

    for k, v in patient_code_age_tuples:
        if k in key_codes:
            if (float(v) >= 0) and (v is not None) and (float(v) < min_age):
                if age_criteria_dict and (float(v) >= age_criteria_dict[k]):
                    continue
                min_age = float(v)
                available_codes.append(k)

    return min_age, available_codes


def merge_dicts(*args):
    return_dict = {}
    for a in args:
        for key in a:
            return_dict[key] = a[key]
    return return_dict
