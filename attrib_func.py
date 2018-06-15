

def single_output_conversion(list_of_values, convert_dict=None, default_value = None, input_value=None):

    return_value = None

    if (not input_value) and len(list_of_values) == 1:
        single_value = list(list_of_values)[0]
        if convert_dict:
            if single_value and (default_value is not None):
                return_value = default_value
            for k in convert_dict:
                if single_value in convert_dict[k]:
                    return_value = k
            return return_value
        else:
            return single_value

    if input_value == 'F':
        next_value = next((v for v in list_of_values), None)
        if next_value == '':
            return None
        if convert_dict:
            if next_value and (default_value is not None):
                return_value = default_value
            for k in convert_dict:
                if next_value in convert_dict[k]:
                    return_value = k

    if input_value == 'A':
        if len(list_of_values) > 0 and (default_value is not None):
            return_value = default_value

        for k in convert_dict:
            if any(patient_val in convert_dict[k] for patient_val in list_of_values):
                return_value = k
                break


    return return_value
