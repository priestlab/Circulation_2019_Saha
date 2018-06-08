# Open HES file and translator file

hes_file = pd.read_csv('hes_all_main_sec_diag.csv')
translator = pd.read_table('eid_translator', sep=',')

hes_translated = pd.merge(hes_file, translator, left_on='eid', right_on='app13721')
hes_translated.drop(['eid', 'app13721'], inplace=True, axis=1)
hes_translated.rename(columns={'app15860':'Patient_ID'}, inplace=True)

icd10_cols = [c for c in hes_translated.columns if 'diag_icd10' in c]
icd9_cols = [c for c in hes_translated.columns if 'diag_icd9' in c]
opcs_cols = [c for c in hes_translated.columns if 'oper4' in c]

print icd10_cols
print icd9_cols
print opcs_cols

for c in icd9_cols:
    hes_translated[c] = hes_translated[c].astype('str')

# Open our file
ukb_file = pd.read_csv('marelli_prehes2.csv')

print "Translated HES File. All Files Loaded"

# Get all patients where CHD = 2 and merge on patient ID
hes_all_patients = pd.merge(ukb_file[['Patient_ID', 'Year_Of_Birth_0_0']], hes_translated, on='Patient_ID')


def get_years(birth_year, *args):
    birth = int(birth_year)
    for a in args:
        if str(a) != 'nan':
            event_year = int(str(a).split('-', 1)[0])
            return event_year - birth_year
    return None

hes_all_patients['icd_years'] = hes_all_patients.apply(lambda row: get_years(row['Year_Of_Birth_0_0'], row['epistart'], row['admidate'], row['epiend'], row['disdate']), axis=1)
hes_all_patients['opcs_years'] = hes_all_patients.apply(lambda row: get_years(row['Year_Of_Birth_0_0'], row['epistart'], row['admidate'], row['opdate'], row['epiend'], row['disdate']), axis=1)

print "Translated Years"

april_1997 = pd.to_datetime('1997-04-01')

hes_all_patients = hes_all_patients[pd.to_datetime(hes_all_patients['epistart']) >= april_1997]
hes_all_patients = hes_all_patients[pd.to_datetime(hes_all_patients['admidate']) >= april_1997]
hes_all_patients = hes_all_patients[pd.to_datetime(hes_all_patients['opdate']) >= april_1997]
hes_all_patients = hes_all_patients[pd.to_datetime(hes_all_patients['epiend']) >= april_1997]
hes_all_patients = hes_all_patients[pd.to_datetime(hes_all_patients['disdate']) >= april_1997]
print len(hes_all_patients)

hes_all_patients.to_csv('hes_main_sec_apr_1997.csv')
