# -*- coding: utf-8 -*-
"""
This script imports existing data for Kazakhstan from an Excel file.
"""

import glob
import os.path
import pandas as pd
import yaml

# Read the excel file.
def read_excel(filename):
    # Read the Excel spreadsheet into a dataframe.
    excel_opts = {
        'sheet_name': None,
        'header': None,
        'names': ['ru', 'en', 'kz'],
        'skiprows': [0],
        'usecols': [0,1,2]
    }
    df = pd.read_excel(os.path.join('scripts', 'batch', filename), **excel_opts)
    return df

def parse_indicator_name(sheet_name):
    sheet_name = sheet_name.strip()
    sheet_name = sheet_name.replace('.', '-')
    sheet_name = sheet_name.replace('Goal', '')
    return sheet_name.strip()


# Get the metadata for an indicator.
def get_metadata(filepath):
    with open(filepath, 'r') as stream:
        try:
            for doc in yaml.safe_load_all(stream):
                if hasattr(doc, 'items'):
                    return doc
        except yaml.YAMLError as e:
            print(e)


def write_metadata(filepath, metadata):
    yaml_string = yaml.dump(metadata,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=True,
        allow_unicode=True)
    with open(filepath, 'w') as outfile:
        outfile.write(yaml_string.replace("\n...\n", "\n---\n"))


spreadsheets = [
    '1.xlsx',
    '2.xlsx',
    '3.xlsx',
    '4.xlsx',
    '5.xlsx',
    '7.xls',
    '8.xls',
    '16-and-17.xls'
]

meta_keys = [
    'source_compilation_1',
    'source_implementation_1',
    'source_data_1',
]

ru = {}
en = {}
kz = {}

for spreadsheet in spreadsheets:
    sheets = read_excel(spreadsheet)
    for sheet_name in sheets:
        df = sheets[sheet_name]
        inid = parse_indicator_name(sheet_name)
        filepath = os.path.join('meta', inid + '.md')
        meta = get_metadata(filepath)
        ru[inid] = {}
        en[inid] = {}
        kz[inid] = {}

        translations_found = 0

        for index, row in df.iterrows():
            # Skip empty cells.
            if row.isnull().values.any():
                continue
            meta_key = meta_keys[index]
            ru[inid][meta_key] = row['ru'].strip()
            en[inid][meta_key] = row['en'].strip()
            kz[inid][meta_key] = row['kz'].strip()
            translations_found += 1

            translation_key = 'sources.' + inid + '.' + meta_key
            meta[meta_key] = translation_key

        if translations_found > 0:
            meta['source_active_1'] = True
            write_metadata(filepath, meta)
        else:
            del ru[inid]
            del en[inid]
            del kz[inid]


write_metadata('en-sources.yml', en)
write_metadata('kz-sources.yml', kz)
write_metadata('ru-sources.yml', ru)
