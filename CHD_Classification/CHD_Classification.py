import csv
import pandas as pd
import config
import op_sheets
import main_func as opf
import hes_func


# From Excel Sheets with Codes of Interest. ------

icd9_mals =  op_sheets.icd9_mals    # INCLUSION
icd10_mals =  op_sheets.icd10_mals
opcs_mals =  op_sheets.opcs_mals
selfrep_mc_mals =  op_sheets.selfrep_mc_mals
selfrep_op_mals =  op_sheets.selfrep_op_mals

icd9_ex_mals =  op_sheets.icd9_ex_mals  # EXCLUSION
icd10_ex_mals =  op_sheets.icd10_ex_mals
opcs_ex_mals =  op_sheets.opcs_ex_mals
selfrep_mc_ex_mals =  op_sheets.selfrep_mc_ex_mals

cond_dict =  op_sheets.cond_dict    # CONDITIONAL EXCLUSION MALFORMATIONS

icd9_cond =  op_sheets.icd9_cond    # CODES FOR CONDITIONAL EXCLUSION MALFORMATIONS
icd10_cond =  op_sheets.icd10_cond
opcs_cond =  op_sheets.opcs_cond
selfrep_mc_cond =  op_sheets.selfrep_mc_cond
selfrep_op_cond =  op_sheets.selfrep_op_cond


icd10_age = op_sheets.icd10_age
icd9_age = op_sheets.icd9_age
opcs_age = op_sheets.opcs_age
selfrep_mc_age =  op_sheets.selfrep_mc_age # AGE CRITIERIA (Self Reported Codes and Ages)
selfrep_op_age =  op_sheets.selfrep_op_age

selfrep_mc_age_mals = op_sheets.selfrep_mc_age_mals
selfrep_op_age_mals = op_sheets.selfrep_op_age_mals

asd_pfo =  op_sheets.asd_pfo    # ASD/PFO Prior To STROKE
stroke = op_sheets.stroke

metacats = op_sheets.metacats   # Meta-Categories
"""
# ----------------------------------------------

# (DO-NOT-CHANGE
f = open(config.ukb_file)
header = f.readline()
headers = header.split('\t')
headers[0] = '0_0'

line_list = []
lines = f.readlines()
f.close()
# DO-NOT-CHANGE)

# Must Specify Field Numbers of Fields of Interest
year_of_birth_index = opf.get_header_indices(headers, '34')

icd10_index = opf.get_header_indices(headers, '41202') + opf.get_header_indices(headers, '41204')
opcs_index = opf.get_header_indices(headers, '41200') + opf.get_header_indices(headers, '41210')
icd9_index = opf.get_header_indices(headers, '41203') + opf.get_header_indices(headers, '41205')
selfrep_mc_index = opf.get_header_indices(headers, '20002', '20009')
selfrep_op_index = opf.get_header_indices(headers, '20004', '20011')


# Names of Columns for Output File
fieldnames = ['Patient_ID']
fieldnames.append('Year_Of_Birth')
fieldnames.append('CHD')
fieldnames.append('Confirmed')
fieldnames.append('Malformation')
fieldnames.append('Keep_Mals')
fieldnames.append('EXCLUDE_IF_NON_CHD')
fieldnames.append('SELFREP_Age_At_CHD')

# A List of Malformations: Patients will be excluded if they have the following AND they do NOT have CHD (CHD = 0).
exclude_if_non_chd = ['THORACIC_AO_DISSECTION', 'ENDOCARDITIS', 'AORTIC_ROOT', 'PULM_HYPERTENSION', 'HEART_TRANSPLANT', 'HCM', 'PERSISTENT_FETAL_CIRCULATION']

# Counters to Keep Track of Each Step
ALL_UKB_COUNT = 0
COMPLETE_EXCLUSION_COUNT = 0
CONFIRMED_COUNT = 0
UNCONFIRMED_COUNT = 0
CONTROL_COUNT = 0
UNCONFIRMED_COUNT_2 = 0
CONTROL_COUNT_2 = 0

print 'There are ' + str(len(lines))+ ' rows in the UKB file. The program will output the total number of lines processed below: '

# 'e' is for displaying how many patient rows we have processed
for e, line in enumerate(lines):

    line = line.split('\t') # We get a list of values after tab-separating the row.

    # Writes the Patient ID to a new line in the file. If there are no more non-blank lines in the file, continue to the next portion
    newline = {'Patient_ID': line[0]}
    if newline['Patient_ID'].isspace() or len(newline['Patient_ID']) == 0:
        break

    # Returns a set of values associated with Year of Birth. Since we know there is only one value, we "pop" that value out of the set
    newline['Year_Of_Birth'] = opf.get_patient_vals(line, year_of_birth_index).pop()

    icd10_line = opf.get_patient_vals(line, icd10_index)
    icd9_line = opf.get_patient_vals(line, icd9_index)
    opcs_line = opf.get_patient_vals(line, opcs_index)
    selfrep_mc_line = opf.get_patient_vals(line, selfrep_mc_index)
    selfrep_op_line = opf.get_patient_vals(line, selfrep_op_index)

    # INCLUSION

    inclusion = opf.match_codes(icd10_mals, icd10_line) +\
    opf.match_codes(icd9_mals, icd9_line) +\
    opf.match_codes(opcs_mals, opcs_line) +\
    opf.match_codes(selfrep_mc_mals, selfrep_mc_line) +\
    opf.match_codes(selfrep_op_mals, selfrep_op_line)

    inclusion = set(inclusion)  # Get the unique malformations (Not Required, but may be faster)


    # EXCLUSION

    exclusion = opf.match_codes(icd10_ex_mals, icd10_line) +\
            opf.match_codes(icd9_ex_mals, icd9_line) +\
            opf.match_codes(opcs_ex_mals, opcs_line) +\
            opf.match_codes(selfrep_mc_ex_mals, selfrep_mc_line)

    # Exclude Patients
    if len(exclusion) > 0:
        COMPLETE_EXCLUSION_COUNT += 1
        continue

    unconfirmed_chd = opf.ends_with(inclusion, '_COND', all_vals = True)

    if (len(inclusion) > 0) and (not unconfirmed_chd):
        newline['CHD'] = 1
        newline['Confirmed'] = 1
        CONFIRMED_COUNT += 1
    elif unconfirmed_chd:
        newline['CHD'] = 2
        newline['Confirmed'] = 0
        UNCONFIRMED_COUNT += 1
    else:
        newline['CHD'] = 0
        newline['Confirmed'] = 0
        CONTROL_COUNT += 1

    # CONDITIONAL MALFORMATIONS

    conditional_mals = opf.match_codes(icd10_cond, icd10_line) +\
            opf.match_codes(icd9_cond, icd9_line) +\
            opf.match_codes(opcs_cond, opcs_line) +\
            opf.match_codes(selfrep_mc_cond, selfrep_mc_line) +\
            opf.match_codes(selfrep_op_cond, selfrep_op_line)


    condition = False
    if unconfirmed_chd:
        non_chd_malformations = opf.has_condition(cond_dict, inclusion, conditional_mals)
        condition = len(non_chd_malformations) > 0  # If there are non_chd_malformations, condition is true

    if unconfirmed_chd and condition:
        newline['CHD'] = 0
        CONTROL_COUNT_2 += 1
        unconfirmed_chd = False
    elif unconfirmed_chd:
        UNCONFIRMED_COUNT_2 += 1


    # Checks Self-Reported Data and sets CHD=1 if Age Criteria is True for Uncertain CHD Patients

    newline['SELFREP_Age_At_CHD'] = 2000 # Default Age Value

    if unconfirmed_chd:

        # patient_codes = [(code, age), (code2, age2), ...] ~ codes with their corresponding ages
        selfrep_mc_codes_and_ages = opf.get_patient_vals(line, selfrep_mc_index, return_both=True)
        selfrep_op_codes_and_ages = opf.get_patient_vals(line, selfrep_op_index, return_both=True)

        # Returns matching CHD codes
        selfrep_mc_chd_codes = opf.match_codes(selfrep_mc_mals.keys(), selfrep_mc_line)
        selfrep_op_chd_codes = opf.match_codes(selfrep_op_mals.keys(), selfrep_op_line)


        # Get both the minimum age and the codes for which the age criteria was met
        mc_min_age, mc_codes_with_age_met = opf.get_min_age(selfrep_mc_codes_and_ages, selfrep_mc_age, age_criteria_dict = selfrep_mc_age)
        op_min_age, op_codes_with_age_met = opf.get_min_age(selfrep_op_codes_and_ages, selfrep_op_age, age_criteria_dict = selfrep_op_age)


        newline['SELFREP_Age_At_CHD'] = min(mc_min_age, op_min_age)

        # Patients have CHD if the age criteria for self-reported conditional malformations is met
        if len(mc_codes_with_age_met) + len(op_codes_with_age_met) > 0:
            newline['CHD'] = 1

        # Converts the codes into Malformations that meet criteria. We make a note to not remove these at the end of the program
        keep_mals = opf.match_codes(selfrep_mc_mals, mc_codes_with_age_met) +  opf.match_codes(selfrep_op_mals, op_codes_with_age_met)
        newline['Keep_Mals'] = ','.join(set(keep_mals))

    # We will exclude non-chd patients at the end of the program if they have any malformations below
    newline['EXCLUDE_IF_NON_CHD'] = opf.match_codes(conditional_mals, exclude_if_non_chd)
    newline['EXCLUDE_IF_NON_CHD'] = ','.join(newline['EXCLUDE_IF_NON_CHD']) # Outputs Python list as comma-separated string of values

    newline['Malformation'] = ','.join(set(inclusion))  # Returns list as comma-separated values

    line_list.append(newline)
    ALL_UKB_COUNT += 1

    if e%25000 == 0:
        print e



print "ALL_UKB_COUNT: " + str(ALL_UKB_COUNT)
print 'COMPLETE_EXCLUSION_COUNT: ' + str(COMPLETE_EXCLUSION_COUNT)
print 'CONFIRMED_COUNT: ' + str(CONFIRMED_COUNT)
print 'UNCONFIRMED_COUNT: ' + str(UNCONFIRMED_COUNT)
print 'CONTROL_COUNT: ' + str(CONTROL_COUNT)
print 'UNCONFIRMED_COUNT_2: ' + str(UNCONFIRMED_COUNT_2)
print 'CONTROL_COUNT_2: ' + str(CONTROL_COUNT_2+CONTROL_COUNT)


with open('UKB_prehes.csv', 'w') as c_file:
    c_writer = csv.DictWriter(c_file, fieldnames=fieldnames)
    c_writer.writeheader()
    c_writer.writerows(line_list)

"""
# --------------------HES---------------------------------

hes_translated = hes_func.translate_file('app13721', 'app15860')

# Indexes the column for each type of code
icd10_cols = [c for c in hes_translated.columns if 'diag_icd10' in c]
icd9_cols = [c for c in hes_translated.columns if 'diag_icd9' in c]
opcs_cols = [c for c in hes_translated.columns if 'oper4' in c]

# Converts ICD9 codes to String
for c in icd9_cols:
    hes_translated[c] = hes_translated[c].astype('str')

# Open our file and merge all unconfirmed CHD Patients with the HES File
ukb_file = pd.read_csv('UKB_prehes.csv')
merge_file = pd.merge(ukb_file[ukb_file['CHD'] == 2][['Patient_ID', 'Year_Of_Birth']], hes_translated, on='Patient_ID')

# -- Calculate Ages --
# - icd_years: (For ICD9 and ICD10), does not take operation date into account
# - opcs_years: (For OPCS), takes all dates into account
merge_file['icd_years'] = merge_file.apply(lambda row: hes_func.get_years(row['Year_Of_Birth'], row['epistart'], row['admidate'], row['epiend'], row['disdate']), axis=1)
merge_file['opcs_years'] = merge_file.apply(lambda row: hes_func.get_years(row['Year_Of_Birth'], row['epistart'], row['admidate'], row['opdate'], row['epiend'], row['disdate']), axis=1)

print "Translated Years"

# Creates an Age Dictionary with Malformations:
age = {}
for k in selfrep_mc_age_mals.keys():
    age[k] = selfrep_mc_age_mals[k]
for k in selfrep_op_age_mals.keys():
    age[k] = selfrep_op_age_mals[k]

print age


# ------------ Define HES functions --------------------------
def has_mal(row, mal_type):
    """ Returns the age at which a patient has codes for Stroke or ASD/PFO for each admission. If there are no codes present, the default value (2000) is returned."""

    if mal_type == 'STROKE':

        # Get all patient ICD codes that match with stroke
        stroke_icd10 = opf.match_codes(stroke['ICD10'].tolist(), [row[c] for c in icd10_cols])
        stroke_icd9 = opf.match_codes(stroke['ICD9'].tolist(), [row[c] for c in icd9_cols])

        if (len(stroke_icd10) > 0) | (len(stroke_icd9) > 0):
            return row['icd_years'] # Returns age at Stroke Diagnosis

    elif mal_type == 'ASD_PFO':

        # Get all patient codes that match with ASD/PFO
        asd_pfo_icd10 = opf.match_codes(asd_pfo['ICD10'].tolist(), [row[c] for c in icd10_cols])
        asd_pfo_icd9 = opf.match_codes(asd_pfo['ICD9'].tolist(), [row[c] for c in icd9_cols])
        asd_pfo_opcs = opf.match_codes(asd_pfo['OPCS'].tolist(), [row[c] for c in opcs_cols])

        if (len(asd_pfo_icd10) > 0) | (len(asd_pfo_icd9) > 0):
            return row['icd_years']
        elif len(asd_pfo_opcs) > 0:
            return row['opcs_years']

    return 2000


def earliest_age_at_diagnosis(stroke, asd_pfo):
    """ Returns 1 if the patient's earliest diagnosis of ASD/PFO occurred before their earliest Stroke"""
    if asd_pfo != 2000:
        if stroke == 2000: # If the patient does not have stroke but has ASD/PFO, chd=1
            return 1
        elif stroke > asd_pfo: # If the patient had a stroke after they had asd/pfo, chd=1
                return 1
        else:
            return 0
    else:
        return 0


def  check_age_criteria(row, patient_codes, codes_of_interest, age_at_disease):
    """ Returns all conditional malformations that pass age criteria """
    keep_mals = []
    for c in patient_codes:
        if row[c] in codes_of_interest.keys():
            malformation = codes_of_interest[row[c]]
            if malformation in age.keys():
                if row[age_at_disease] < int(age[malformation]):
                    keep_mals.append(malformation)

    return keep_mals


def malfomations_passing_age_criteria(row):
    """ Returns a set of malformations that have all passed age criteria"""
    keep_mals = []

    keep_mals.extend(check_age_criteria(row, icd10_cols, icd10_mals, 'icd_years'))
    keep_mals.extend(check_age_criteria(row, icd9_cols, icd9_mals, 'icd_years'))
    keep_mals.extend(check_age_criteria(row, opcs_cols, opcs_mals, 'opcs_years'))

    return ','.join(set(keep_mals))


def reassign_mals(chd, existing_mals, keep_mals, asd_pfo_true):
    """ Adds/Keeps Malformations that meet age criteria and ASD/PFO criteria. Removes all malformations if CHD = 0. """

    # Turn the comma-separated string of malformations into a list of malformations. If the string is null it will be of type float and return None
    if type(existing_mals) != float:
        exist = existing_mals.split(',')
    else:
        return None

    if type(keep_mals) == float:
        keep_mals = ''  # Null values are floats. Turns this value into string

    # Make a list of all possible malformations to remove
    remove = [mal for mal in age.keys() if mal not in set(keep_mals.split(','))]
    if asd_pfo_true == 0:
        remove.append('ASD_PFO_COND')

    # Delete all malformations if CHD = 0 and no conditional malformation criteria was met.
    if (keep_mals == '') and (asd_pfo_true == 0) and (chd == 0):
        return None

    # Remove unneeded malformations from original UKB file
    inc_mal = [mal for mal in exist if mal not in remove]

    # Some patients may have had conditional malformations that did not exist in the main UKB file, but did exist in HES. If criteria is met, these malformations are added.
    for k in keep_mals.split(','):
        if k not in inc_mal:
            inc_mal.append(k)
    if ((asd_pfo_true == 1) and ('ASD_PFO_COND' not in inc_mal)):
        inc_mal.append('ASD_PFO_COND')

    return ','.join(inc_mal)

# --------------------------------------------------


# Assigns patients with the age at which they had a stroke or asd_pfo for an admission. Assigns malformations to patient admission if they meet age criteria
merge_file['has_stroke'] = merge_file.apply(lambda row: has_mal(row, 'STROKE'), axis=1)
merge_file['has_asd_pfo'] = merge_file.apply(lambda row: has_mal(row, 'ASD_PFO'), axis=1)
merge_file['Keep_Mals'] = merge_file.apply(lambda row: malfomations_passing_age_criteria(row), axis=1)


# GROUPS BY PATIENT ID.
# - Gets the minimum age for ASD/PFO and STROKE across all admissions
# - Concatenates the Malformations that Met Age Criteria for all admissions
grouped_patients = merge_file.groupby('Patient_ID').agg(dict(has_stroke = 'min',
                   has_asd_pfo = 'min',
                   Keep_Mals = lambda x: '%s'%','.join(x))).reset_index()

grouped_patients['Keep_Mals'] = grouped_patients['Keep_Mals'].apply(lambda mals: ','.join({x for x in mals.split(',') if len(x) > 0}))


# Checks if the earliest ASD/PFO did not have strokes prior to it
grouped_patients['ASD_PFO_TRUE'] = grouped_patients.apply(lambda row: earliest_age_at_diagnosis(row['has_stroke'], row['has_asd_pfo']), axis=1)



# Merge the original UKB file with the data from HES file
ukb_file2 = pd.merge(ukb_file, grouped_patients, on='Patient_ID', how='left')
print ukb_file2.columns


# Combine Malformations with criteria met from self-reported data and HES data
ukb_file2['Keep_Mals'] = ukb_file2.apply(lambda row: ','.join({mal for mal in (row['Keep_Mals_x'],row['Keep_Mals_y']) if ((mal != '') and (type(mal)!=float))}), axis=1)

ukb_file2.drop(['Keep_Mals_x', 'Keep_Mals_y'], axis=1, inplace=True)    # Remove redundant variables

# Assigns official malformations which include conditional and unconditional malformations
ukb_file2['Malformation'] = ukb_file2.apply(lambda row: reassign_mals(row['CHD'], row['Malformation'], row['Keep_Mals'], row['ASD_PFO_TRUE']), axis=1)


# Assign CHD based on criteria check
ukb_file2['CHD'] = ukb_file2.apply(lambda row: 1 if (((type(row['Keep_Mals']) != float) and (row['Keep_Mals'] != '')) or (row['ASD_PFO_TRUE'] == 1) or (row['CHD'] == 1)) else 0, axis=1)

# Print the Counts
print 'AGE CRITERIA: ' + str(len(grouped_patients[grouped_patients['Keep_Mals'] != '']['Patient_ID'].unique()))
print 'ASD/PFO CRITERIA: ' + str(len(grouped_patients[grouped_patients['ASD_PFO_TRUE'] == 1]['Patient_ID'].unique()))
print 'CONFIRMED_COUNT_3: ' + str(len(ukb_file2[ukb_file2['CHD'] == 1]['Patient_ID'].unique()))
print 'CONTROL_COUNT_3: ' + str(len(ukb_file2[ukb_file2['CHD'] == 0]['Patient_ID'].unique()))
print 'CONTROL_COUNT_FINAL: ' + str(len(ukb_file2[(ukb_file2['CHD'] == 0)&(ukb_file2['EXCLUDE_IF_NON_CHD']==False)]['Patient_ID'].unique()))

# Assigns metacategory based on malformation
ukb_file2['MetaCategory'] = ukb_file2['Malformation'].apply(lambda all_mals: ','.join(sorted({metacats[x] for x in all_mals.split(',') if x in metacats.keys()})) if all_mals else None)

# Drops irrelevant columns
ukb_file2.drop(['has_asd_pfo', 'has_stroke', 'ASD_PFO_TRUE', 'Keep_Mals'], axis=1, inplace=True)

# Removes control patients from dataset if they have malformations we want to exclude
ukb_file2[(ukb_file2['CHD']==0) & (~ukb_file2['EXCLUDE_IF_NON_CHD'].isna())].to_csv("UKB.csv")
