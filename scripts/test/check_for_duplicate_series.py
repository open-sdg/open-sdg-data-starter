import sdg
import os
import pandas as pd

debug = 'foo'
duplicates = {}

ids = sdg.path.get_ids()
for inid in ids:
    df = sdg.data.get_inid_data(inid)
    columns = df.columns.to_list()
    columns.remove('Value')
    duplicateRows = df[df.duplicated(subset=columns)]
    if len(duplicateRows):
        if debug == inid:
            print(duplicateRows)
        duplicates[inid] = duplicateRows
        #print(duplicateRows)

#pd.set_option('display.max_columns', 30)
#print(len(duplicates.keys()))
print(duplicates['4-5-1'].to_string())
print(duplicates.keys())
#print(duplicates)
