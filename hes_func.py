import pandas as pd
import config


def translate_file(current_appID, desired_appID):
    """ Uses a comma-separated UKB translator file to convert patient ids from the current application HES file to patient ids from the desired appliacation HES file."""
    # Translates HES File
    hes_file = pd.read_csv(config.hes_file)
    translator = pd.read_table(config.hes_translator, sep=',')

    hes_translated = pd.merge(hes_file, translator, left_on='eid', right_on=current_appID)
    hes_translated.drop(['eid', current_appID], inplace=True, axis=1)
    hes_translated.rename(columns={desired_appID:'Patient_ID'}, inplace=True)

    return hes_translated


def get_years(birth_year, *args):
    """ This function takes multiple date arguments and subtracts the year of the date by the birth year. It will return the first valid age, otherwise it will return 2000."""

    # Gets the age value at which the event happened
    birth = int(birth_year)
    for a in args:  # args refer to the possible dates
        if str(a) != 'nan':
            # Gets the year of the event date (e.g. 2000-01-01)
            event_year = int(str(a).split('-', 1)[0])
            return event_year - birth_year
    return 2000
