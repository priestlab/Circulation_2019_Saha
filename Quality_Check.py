import pandas as pd

old_df = pd.read_csv('RandomExtract1.csv')
new_df = pd.read_csv('RandomExtract2.csv')

cols = [c for c in new_df.columns if c in old_df]

mdf = pd.merge(old_df[old_df['CHD']==1][cols], new_df[cols], on='Patient_ID')

concatenated_columns = ['Malformation', 'MetaCategory']


def check_count(this_df, df_name, column_name):
    """Use this function if entries in column are comma-separated values"""
    print df_name
    print column_name
    print '\n'

    unique_entries = this_df[column_name].unique()

    for m in sorted(unique_entries):
        if type(m) != float:
            print m+': '+str(len(this_df[this_df[column_name] == m]))
    print '\n'


for c in cols:
    if c in concatenated_columns:
        check_count(old_df[old_df['CHD'] == 0], 'Old Data', c)
        check_count(new_df, 'New Data', c)

print 'Number of Mismatched Entries By Column'
for c in cols:
    if (c != 'Patient_ID') and (c not in concatenated_columns):
        print c
        match_df = mdf[mdf[c+'_x'] != mdf[c+'_y']][['Patient_ID', c+'_x', c+'_y']].dropna()
        print len(match_df)
        print match_df.head()
        print '\n'
