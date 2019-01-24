# -*- coding: utf-8 -*-
"""
This script imports existing data for Armenia from an Excel file.
"""

import glob
import os.path
import pandas as pd
import numpy as np
import yaml

# For more readable code below.
HEADER_YEAR = 'Year'
HEADER_VALUE = 'Value'
HEADER_UNIT = 'Units'
FOLDER_DATA_CSV = 'data'
FOLDER_METADATA_YAML = 'meta'

YEARS = ['2015', '2016', '2017']

HARDCODED_DISAGGREGATION_COLUMNS = {
    'participants': 'Employment status',
    'economically inactive  population': 'Employment status',
    'pensioners': 'Employment status',
    'students': 'Employment status',
    'other inactive population': 'Employment status',
    'non-participants': 'Employment status',
}

WILDCARD_DISAGGREGATION_COLUMNS = {
    'male': 'Sex',
    'female': 'Sex',
    'rural': 'Location',
    'urban': 'Location',
    'older': 'Age',
    '+': 'Age',
    'before age': 'Age',
    'employ': 'Employment status',
    'education': 'Education type',
    'primary': 'Education type',
    'secondary': 'Education type',
    'high': 'Education type',
    'vocational': 'Education type',
    'bachelor': 'Education type',
    'master': 'Education type',
    'transport': 'Transportation type',
    'disaster': 'Disaster type',
}

# For random typos and tweaks. Used as regex, so special characters need escaping.
GENERAL_REPLACEMENTS = {
    '10\.7\.2\. a': '10.7.2.a',
    '10\.7\.2\. b': '10.7.2.b',
    '5\.a\.1 \(a\)\.a': '5.a.1.a.a',
    '5\.a\.1 \(b\)\.a\.1': '5.a.1.b.a.1',
    '5\.a\.1 \(b\)\.a\.2': '5.a.1.b.a.2',
    'agee': 'age',
    '–': '-',
}

# Helper function to return some text without certain words.
def strip_words(text, words):
    for word in words:
        text = text.replace(word, '')
    return text.strip()

# Figure out from a category value what the name of the column should be.
def get_disaggregation_column(category):
    category = category.lower()
    ret = False
    for wildcard in WILDCARD_DISAGGREGATION_COLUMNS:
        # Look for general wildcards to figure out the column name.
        if wildcard in category:
            ret = WILDCARD_DISAGGREGATION_COLUMNS[wildcard]
            break
    if not ret:
        # Consult a hardcoded list.
        if category in HARDCODED_DISAGGREGATION_COLUMNS:
            ret = HARDCODED_DISAGGREGATION_COLUMNS[category]

    if not ret:
        # Some more detailed checks follow.

        # See if this is 2 integers separated by "to" or "-".
        ignore = ['years', 'year', 'aged', 'age']
        for sep in ['to', '-']:
            words = category.split(sep)
            if len(words) > 1:
                if all(strip_words(word, ignore).isdigit() for word in words):
                    ret = 'Age'
                    break
    if not ret:
        ret = 'Category'

    return ret

# Start off a dataframe for an indicator.
def blank_dataframe(disaggregations):
    """This starts a blank dataframe with our required tidy columns."""

    # Start with two columns, year and value.
    structure = {}
    structure[HEADER_YEAR] = []
    structure[HEADER_UNIT] = []
    for disaggregation in disaggregations:
        structure[disaggregation] = []
    structure[HEADER_VALUE] = []
    blank = pd.DataFrame(structure)
    # Make sure the year column is typed for integers.
    blank[HEADER_YEAR] = blank[HEADER_YEAR].astype(int)

    return blank

# Write a dataframe to disk as a CSV file.
def write_csv(id, df):

    csv_filename = 'indicator_' + id.replace('.', '-') + '.csv'

    try:
        path = os.path.join(FOLDER_DATA_CSV, csv_filename)
        df.to_csv(path, index=False, encoding='utf-8')
    except Exception as e:
        print(id, e)
        return False

    return True

# Get an indicator ID from the beginning of some text, if it is there.
def indicator_id(text):
    ret = False
    if isinstance(text, str):
        words = text.split(' ')
        id = words[0]
        if '.' in id:
            if id.endswith('.'):
                id = id[:-1]
            ret = id
    return ret

# Create a dict representing one row in ultimate CSV file.
def get_csv_row(year, disaggregations, value, unit):
    ret = {}
    ret[HEADER_YEAR] = year
    ret[HEADER_UNIT] = unit
    for disaggregation in disaggregations:
        ret[disaggregation] = disaggregations[disaggregation]
    ret[HEADER_VALUE] = value
    return ret

# Read the excel file.
def read_excel():
    # Read the Excel spreadsheet into a dataframe.
    excel_opts = {
      'header': None,
      'names': ['Global', 'National', 'Unit', '2015', '2016', '2017', 'Source'],
      'skiprows': [0, 1],
      'usecols': [2,3,4,5,6,7,8]
    }
    df = pd.read_excel('SDG_eng.xlsx', **excel_opts)
    return df

# Helper function to get a slice of the main dataframe for one indicator.
def get_indicator_dataframe(df, indicator_info):
    start = indicator_info['start']
    end = indicator_info['end']
    return df[start:end + 1]

# Get the metadata for an indicator.
def get_metadata(filepath):
    with open(filepath, 'r') as stream:
        try:
            # Currently the YAML in `meta` has "front matter" and "content",
            # and we only want the "front matter". So we have to get a bit
            # fancy below.
            for doc in yaml.safe_load_all(stream):
                if hasattr(doc, 'items'):
                    return doc
        except yaml.YAMLError as e:
            print(e)

def get_indicator_sort_order(id):
    parts = id.split('.')
    ret = []
    for part in parts:
        if len(part) < 2:
            part = '0' + part
        ret.append(part)
    return '-'.join(ret)

def write_indicator_for_site_repo(metadata):
    indicator = metadata['indicator'].replace('.', '-')
    output = {
        'indicator': metadata['indicator'],
        'layout': 'indicator',
        'permalink': '/' + indicator + '/',
    }

    # Write to a string first because I want to override trailing dots
    yaml_string = yaml.dump(output,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=True)
    # Create the place to put the files.
    folder = 'move-to-site-repo'
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, indicator + '.md')
    with open(filepath, 'w') as outfile:
        outfile.write(yaml_string.replace("\n...\n", "\n---\n"))

    # Lets also output some text that we can copy into a YAML file for the
    # purposes of translation.
    print('' + metadata['indicator'] + ':')
    print('  title: ' + metadata['indicator_name'])

def write_metadata(id, df, indicator_info):
    required_metdata = {
        'data_non_statistical': False,
        'graph_type': 'line',
        'published': True,
        'reporting_status': 'complete',
    }
    source = df.iloc[indicator_info['start']]['Source']
    name = df.iloc[indicator_info['start']]['CategoryOriginal']
    name = name.replace(id, '').strip().strip('.').strip()

    filename = id.replace('.', '-') + '.md'
    filepath = os.path.join(FOLDER_METADATA_YAML, filename)

    if os.path.isfile(filepath):
        metadata = get_metadata(filepath)
        # Set the name and graph title.
        metadata['indicator_name'] = name
        metadata['graph_title'] = name
        # Make sure this is set to "complete".
        metadata['reporting_status'] = 'complete'
        # Set the source if needed.
        if isinstance(source, str):
            source = source.replace('\n', ' ').strip()
            metadata['source_active_1'] = True
            metadata['source_organisation_1'] = source
    else:
        metadata = required_metdata
        # Set the name and graph title.
        metadata['indicator_name'] = name
        metadata['graph_title'] = name
        # Make sure this is set to "complete".
        metadata['reporting_status'] = 'complete'
        # Set the source if needed.
        if isinstance(source, str):
            source = source.replace('\n', ' ').strip()
            metadata['source_active_1'] = True
            metadata['source_organisation_1'] = source
        metadata['indicator'] = id
        metadata['indicator_sort_order'] = get_indicator_sort_order(id)
        # Set the goal and target.
        parts = id.split('.')
        metadata['sdg_goal'] = parts[0]
        metadata['target_id'] = parts[0] + '.' + parts[1]
        # While here, let's create some files for the site repository.
        write_indicator_for_site_repo(metadata)

    # Write to a string first because I want to override trailing dots
    yaml_string = yaml.dump(metadata,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=True)
    with open(filepath, 'w') as outfile:
        outfile.write(yaml_string.replace("\n...\n", "\n---\n"))

def main():
    """Tidy up all of the indicator CSVs in the data folder."""

    status = True

    # Create the place to put the files.
    os.makedirs(FOLDER_DATA_CSV, exist_ok=True)

    # Get the source data.
    df = read_excel()

    # Some indicators are already properly disaggregated in the source data.
    already_disaggregated = [
        '2.2.2',
        '8.5.2',
        '8.6.1'
    ]

    # Do some general replacements.
    for search in GENERAL_REPLACEMENTS:
        df = df.replace(search, GENERAL_REPLACEMENTS[search], regex=True)

    # Merge 'Global' and 'National' to a 'Category' column.
    df['Category'] = np.where(df.National.isnull(), df.Global, df.National)
    df['CategoryOriginal'] = df['Category']
    df = df.drop(labels=['Global', 'National'], axis='columns')

    # Remove rows without value in Category.
    df = df.dropna(subset=['Category'], how='all')

    # NOTE: The total number of rows should not change after this point. We
    # reset the index now for logical sequential indexes.
    df = df.reset_index(drop=True)

    # Figure out where each indicator starts and set the ID.
    indicators = {}
    last_id = False
    last_index = False
    for row in df.iterrows():
        index = row[0]
        category = row[1]['Category']
        id = indicator_id(category)
        if not id:
            last_index = index
            continue
        if id in indicators:
            # If we have already set this indicator, something is wrong. So
            # make a note.
            print('Duplicate indicator? ' + id + ' -- ' + category)
        else:
            indicators[id] = {
                'start': index
            }
            # Also set end rows.
            if last_id and last_index:
                indicators[last_id]['end'] = last_index
            last_id = id
            last_index = index
            # Replace the cell data with just the id number.
            df.set_value(index, 'Category', id)
    # Set the last end row.
    for id in indicators:
        if 'end' not in indicators[id]:
            indicators[id]['end'] = df.last_valid_index()
        # For ease later, add the number of rows.
        indicators[id]['num_rows'] = indicators[id]['end'] - indicators[id]['start'] + 1

    # Remove whitespace from Category and Unit values.
    df['Category'] = df['Category'].str.strip()
    df['Unit'] = df['Unit'].str.strip()

    # More normalization replacements.
    replacements = {
        'boy': 'Male',
        'girl': 'Female',
        'men': 'Male',
        'women': 'Female',
        'urban': 'Urban',
        'rural': 'Rural'
    }
    for row in df.iterrows():
        category = row[1]['Category']
        category = category.lower()

        # Skip rows with commas, as those seem to be fine already.
        if ',' in category:
            continue

        for replacement in replacements:
            if replacement in category:
                df.set_value(row[0], 'Category', replacements[replacement])

    # Figure out which rows are disaggregations. Only look for Male/Female.
    for id in indicators:
        indicator_df = get_indicator_dataframe(df, indicators[id])
        # Skip indicators with only one row, as they have no disaggregation.
        if len(indicator_df) == 1:
            continue

        # For indicators that already have sufficient disaggregation, we just
        # convert the commas to pipes.
        if id in already_disaggregated:
            for row in indicator_df.iterrows():
                index = row[0]
                category = row[1]['Category']
                category = category.replace(',', '|')
                df.set_value(index, 'Category', category)

        # Since we're only looking for Male/Female disaggregation, we can also
        # skip any rows that have 1 or less instances of 'Male' or 'Female'.
        num_male = indicator_df['Category'].str.count('Male').sum()
        num_female = indicator_df['Category'].str.count('Female').sum()
        if num_male < 2 and num_female < 2:
            continue

        first_male_found = False
        first_female_found = False
        last_non_gender_category = False
        for row in indicator_df.iterrows():
            index = row[0]
            category = row[1]['Category']
            if category == 'Male':
                if not first_male_found:
                    first_male_found = True
                    continue
            if category == 'Female':
                if not first_female_found:
                    first_female_found = True
                    continue
            if category != 'Male' and category != 'Female':
                last_non_gender_category = category
            else:
                # We need to update the main dataframe by combining this
                # Male/Female with whatever the last non-gender category was,
                # separated by a pipe.
                disaggregated_category = '|'.join([category, last_non_gender_category])
                df.set_value(index, 'Category', disaggregated_category)

    # Finally loop through the indicators and create CSV files.
    for id in indicators:
        # For debugging particular indicators.
        debug = False
        #if id == '1.3.1.a':
        #    debug = True
        # Take a slice of the main dataframe for this indicator.
        indicator_df = get_indicator_dataframe(df, indicators[id])
        all_disaggregations = []
        csv_rows = []
        for row in indicator_df.iterrows():
            category = row[1]['Category']
            unit = row[1]['Unit']
            disaggregations = {}
            if id == category:
                # This is the aggregate total. If this has no values, then we
                # have to skip the whole indicator. Make a note of this.
                foo = 'bar'
            # Split disaggregations into separate rows.
            else:
                for disaggregation in category.split('|'):
                    disaggregation = disaggregation.strip()
                    disaggregation_column = get_disaggregation_column(disaggregation)
                    # Only use the disaggregation if it has at least one value.
                    if any(not isinstance(row[1][year], str) and not np.isnan(row[1][year]) for year in YEARS):
                        if disaggregation_column not in all_disaggregations:
                            all_disaggregations.append(disaggregation_column)
                        disaggregations[disaggregation_column] = disaggregation
            for year in YEARS:
                value = row[1][year]
                if not isinstance(value, str) and not np.isnan(value):
                    csv_row = get_csv_row(year, disaggregations, value, unit)
                    csv_rows.append(csv_row)
        csv_df = blank_dataframe(all_disaggregations)
        for row in csv_rows:
            csv_df = csv_df.append(row, ignore_index=True)

        if not csv_df.empty:
            write_csv(id, csv_df)
            # If we wrote a CSV, we also need to write metadata.
            write_metadata(id, df, indicators[id])

    return status

if __name__ == '__main__':
    if not main():
        raise RuntimeError("Failed tidy conversion")
    else:
        print("Success")