import ast

def to_Dict(sheet_dict):
    """ Will convert values that appear to be dictionaries into Python dictionaries. All values inside the dictionary will be converted to lists with string values. """

    for key in sheet_dict:
        if str(sheet_dict[key]) != 'nan':
            try:
                # If a dictionary is detected in the sheet values, it will create a dictionary
                val = sheet_dict[key].encode('ascii')
                if type(ast.literal_eval(val)) == dict:
                    sheet_dict[key] = ast.literal_eval(val)
                print "Converted value of "+ str(key) + " to dictionary"

                # Converts values in dictionary into a list where each value is a string
                for subkey in sheet_dict[key]:
                    if type(sheet_dict[key][subkey]) != list:
                        sheet_dict[key][subkey] = [str(sheet_dict[key][subkey])] # Turns single value into a list
                    else:
                        sheet_dict[key][subkey] = [str(v) for v in sheet_dict[key][subkey]]
            except:
                continue
        else:
            sheet_dict[key] = None

    sheet_dict = {str(k):sheet_dict[k] for k in sheet_dict.keys()}

    return sheet_dict

def sheet_to_dict(reader, sheet, keys_column, value_column, converters = None, dict_values = False):
    """The program outputs a dictionary based on two columns in an Excel Sheet."""

    c_df = reader.parse(sheet, converters = converters)

    sheet_dict = dict(zip(c_df[keys_column].dropna(), c_df[value_column]))

    for key in sheet_dict:
        if str(sheet_dict[key]) == 'nan':
            sheet_dict[key] = None

    # If your values contain a string representation of a dictionary, convert it to a dictionary
    if dict_values:
        sheet_dict = to_Dict(sheet_dict)

    return sheet_dict


def sheet_to_tuple(reader, sheet, keys_column, value_column, converters = None, dict_values = False):
    """The program outputs a list of tuples based on two columns in an Excel Sheet."""

    c_df = reader.parse(sheet, converters = converters)

    sheet_tuple = zip(c_df[keys_column].dropna(), c_df[value_column].dropna())

    return sheet_tuple
