import pandas as pd

hes_file_oper4 = pd.read_csv('hes_data/app1372_dbtable_hesin_oper_2017aug22.tsv', sep='\t')
hes_file_icd10 = pd.read_csv('hes_data/app1372_dbtable_hesin_diag10_2017aug22.tsv', sep='\t')
hes_file_icd9 = pd.read_csv('hes_data/app1372_dbtable_hesin_diag9_2017aug22.tsv', sep='\t')
hes_file_main = pd.read_csv('hes_data/app1372_dbtable_hesin_2017aug22.tsv', sep='\t')

hes_file_oper4.loc[((hes_file_oper4.eid == 1084380)&(hes_file_oper4.record_id == 3174880)&(hes_file_oper4.oper4 == 'S524')), 'arr_index'] = -1
hes_file_oper4.loc[((hes_file_oper4.eid == 1084380)&(hes_file_oper4.record_id == 723113)&(hes_file_oper4.oper4 == 'S524')), 'arr_index'] = -1
hes_file_icd10.loc[((hes_file_icd10.eid == 3661708)&(hes_file_icd10.record_id == 1536294)&(hes_file_icd10.diag_icd10 == 'U511')), 'arr_index'] = -1

hes_file_oper4['arr_index'] = hes_file_oper4['arr_index'].apply(lambda x: 'oper4_'+str(x+1))
hes_file_icd10['arr_index'] = hes_file_icd10['arr_index'].apply(lambda x: 'diag_icd10_'+str(x+1))
hes_file_icd9['arr_index'] = hes_file_icd9['arr_index'].apply(lambda x: 'diag_icd9_'+str(x+1))


oper4_mod = hes_file_oper4.groupby(["eid","record_id","arr_index"])['oper4'].aggregate(lambda x: x).unstack().reset_index()
oper4_mod.columns=oper4_mod.columns.tolist()
ordered_arr = ['eid', 'record_id']
for a in hes_file_oper4['arr_index'].unique():
    ordered_arr.append(a)
oper4_mod = oper4_mod.reindex_axis(ordered_arr, axis=1)
hes_file = pd.merge(hes_file_main, oper4_mod, on=['eid', 'record_id'], how='left')

icd10_mod = hes_file_icd10.groupby(["eid","record_id","arr_index"])['diag_icd10'].aggregate(lambda x: x).unstack().reset_index()
icd10_mod.columns=icd10_mod.columns.tolist()
ordered_arr = ['eid', 'record_id']
for a in hes_file_icd10['arr_index'].unique():
    ordered_arr.append(a)
icd10_mod = icd10_mod.reindex_axis(ordered_arr, axis=1)
hes_file = pd.merge(hes_file, icd10_mod, on=['eid', 'record_id'], how='left')

icd9_mod = hes_file_icd9.groupby(["eid","record_id","arr_index"])['diag_icd9'].aggregate(lambda x: x).unstack().reset_index()
icd9_mod.columns=icd9_mod.columns.tolist()
ordered_arr = ['eid', 'record_id']
for a in hes_file_icd9['arr_index'].unique():
    ordered_arr.append(a)
icd9_mod = icd9_mod.reindex_axis(ordered_arr, axis=1)
hes_file = pd.merge(hes_file, icd9_mod, on=['eid', 'record_id'], how='left')

print hes_file.head()
hes_file.to_csv('hes_all_main_sec_diag.csv')
