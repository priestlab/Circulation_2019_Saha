import sys
import csv
import pandas as pd
import numpy as np
import time

odf = pd.read_csv('fixed_op_premod.csv')
ndf = pd.read_csv('fixed_op_compare_premod.csv')

odf['Age_At_CHD_SELFREP'] = odf['Age_At_CHD_SELFREP'].apply(lambda x: 2000 if x == 'NANA' else x)
odf['Age_At_CHD_SELFREP'] = odf['Age_At_CHD_SELFREP'].astype('float64')

mdf = pd.merge(odf[['Patient_ID', 'Age_At_CHD_SELFREP']], ndf[['Patient_ID', 'Age_At_CHD_SELFREP']], on='Patient_ID')

print len(odf)
print len(ndf)
print len(mdf)

print '\n'
print mdf[mdf['Age_At_CHD_SELFREP_x'] != mdf['Age_At_CHD_SELFREP_y']]
