import pandas as pd
import config
import ast
import sheets as sh

reader = pd.ExcelFile(config.codes_sheet)
sheets = reader.sheet_names

for s in sheets:
        # INCLUSION CODES SHEETS
    if s == 'CHD_ICD9':
        icd9_mals = sh.sheet_to_dict(reader, s, 'ICD9', 'MALFORMATION', {'ICD9': str})
        icd9_age = sh.sheet_to_dict(reader, s, 'ICD9', 'AGE', {'ICD9': str})    # Age Criteria
    elif s == 'CHD_ICD10':
        icd10_mals = sh.sheet_to_dict(reader, s, 'ICD10', 'MALFORMATION')
        icd10_age = sh.sheet_to_dict(reader, s, 'ICD10', 'AGE')    # Age Criteria
    elif s == 'CHD_OPCS':
        opcs_mals = sh.sheet_to_dict(reader, s, 'OPCS', 'MALFORMATION')
        opcs_age = sh.sheet_to_dict(reader, s, 'OPCS', 'AGE')    # Age Criteria
    elif s == 'CHD_SELFREP_MC_20002':
        selfrep_mc_mals = sh.sheet_to_dict(reader, s, 'CODE', 'MALFORMATION', {'CODE': str})
        selfrep_mc_age = sh.sheet_to_dict(reader, s, 'CODE', 'AGE', {'CODE': str})    # Age Criteria (Diagnoses)
        selfrep_mc_age_mals = sh.sheet_to_dict(reader, s, 'MALFORMATION', 'AGE')
    elif s == 'CHD_SELFREP_OP_20004':
        selfrep_op_mals = sh.sheet_to_dict(reader, s, 'CODE', 'MALFORMATION', {'CODE': str})
        selfrep_op_age = sh.sheet_to_dict(reader, s, 'CODE', 'AGE', {'CODE': str})    # Age Criteria (Operations)
        selfrep_op_age_mals = sh.sheet_to_dict(reader, s, 'MALFORMATION', 'AGE')

        # EXCLUSION CODES SHEETS
    elif s == 'CHD_ICD9_EXCLUSION':
        icd9_ex_mals = sh.sheet_to_dict(reader, s, 'ICD9', 'MALFORMATION', {'ICD9': str})
    elif s == 'CHD_ICD10_EXCLUSION':
        icd10_ex_mals = sh.sheet_to_dict(reader, s, 'ICD10', 'MALFORMATION')
    elif s == 'CHD_OPCS_EXCLUSION':
        opcs_ex_mals = sh.sheet_to_dict(reader, s, 'OPCS', 'MALFORMATION')
    elif s == 'CHD_SELFREP_MC_20002_EXCLUSION':
        selfrep_mc_ex_mals = sh.sheet_to_dict(reader, s, 'CODE', 'MALFORMATION', {'CODE': str})

        # CONDITIONAL EXCLUSION MALFORMATIONS MAIN SHEET
    elif s == 'CHD_CONDITIONAL_EXCLUSIONS_2':
        cond_dict = sh.sheet_to_tuple(reader, s, 'MALFORMATION', 'EXCLUSION CRITERIA')

        # CORRESPONDING CONDITIONAL CODES EXCLUSION SHEETS
    elif s == 'CHD_ICD9_COND_EX':
        icd9_cond = sh.sheet_to_dict(reader, s, 'ICD9', 'MALFORMATION', {'ICD9': str})
    elif s == 'CHD_ICD10_COND_EX':
        icd10_cond = sh.sheet_to_dict(reader, s, 'ICD10', 'MALFORMATION')
    elif s == 'CHD_OPCS_COND_EX':
        opcs_cond = sh.sheet_to_dict(reader, s, 'OPCS', 'MALFORMATION')
    elif s == 'CHD_SELFREP_OP_20004_COND_EX':
        selfrep_op_cond = sh.sheet_to_dict(reader, s, 'CODE', 'MALFORMATION', {'CODE': str})
    elif s == 'CHD_SELFREP_MC_20002_COND_EX':
        selfrep_mc_cond = sh.sheet_to_dict(reader, s, 'CODE', 'MALFORMATION', {'CODE': str})

        # ASD/PFO and STROKE CODES SHEETS to check: ASD/PFO Prior To STROKE
    elif s == 'CHECK_ASD_PFO':
        c_df = reader.parse(s, converters={'ICD9': str})
        asd_pfo = {
                'ICD10': c_df['ICD10'].unique(), # Gets all Unique Values from this column
                'OPCS': c_df['OPCS'].unique(),
                'ICD9': c_df['ICD9'].unique()
                }

    elif s == 'STROKE':
        c_df = reader.parse(s, converters={'ICD9': str, 'SELFREP_MC_20002': str, 'SELFREP_OP_20004': str})
        stroke = {
                'ICD10': c_df['ICD10'].unique(),
                'OPCS': c_df['OPCS'].unique(),
                'ICD9': c_df['ICD9'].unique(),
                'SELFREP_MC_20002': c_df['SELFREP_MC_20002'].unique(),
                'SELFREP_OP_20004': c_df['SELFREP_OP_20004'].unique()
                }

    elif s == 'CHD_METACATEGORIES':
        metacats = sh.sheet_to_tuple(reader, s, 'METACATEGORY', 'MALFORMATIONS')
