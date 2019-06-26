# -*- coding: utf-8 -*-
"""
This script imports existing data for Kazakhstan from an Excel file.
"""

import glob
import os.path
import pandas as pd
import numpy as np
import yaml

DEBUG = False
DEBUG_INDICATOR = '5.3.1'
#DEBUG_INDICATOR = False
def alert(message):
    if DEBUG:
        print(message)

# These global objects will be read/written from various functions, so need to
# be created here.
indicator_map = {}
disagg_table = {}
meta_translations = {}
disagg_mismatches = {}
disagg_mismatches_with_data = {}
single_disagg_values = {}
units = {}
disagg_matches = {}

# For more readable code below.
HEADER_YEAR = 'Year'
HEADER_VALUE = 'Value'
HEADER_UNIT = 'Units'
FOLDER_DATA_CSV = 'data'
FOLDER_METADATA_YAML = 'meta'

# Info about columns in the source data.
YEARS = ['2010','2011','2012','2013','2014','2015','2016','2017','2018']
METADATA = ['source','compilation','implementation','customisation','classification','availability']

# Fix disaggregation values.
def fix_disaggregation(disagg):
    disagg_fixes = {
        '1,9 доллара США по ППС в  день': '1,9 долларов США по ППС в  день',
        'г. Нур-Султан': 'г.Нур-Султан',
        'г. Алматы': 'г.Алматы',
        'г. Шымкент': 'г.Шымкент',
        15: '15',
        'регион': 'Регионы',
        'Перевезено грузов воздушным транспортом': 'перевезено грузов воздушным транспортом',
        'Показатели работы морского и прибрежного транспорта': 'показатели работы морского и прибрежного транспорта',
        'Показатели работы трубопроводного транспорта': 'показатели работы трубопроводного транспорта',
        'Перевезено пассажиров воздушным транспортом': 'перевезено пассажиров воздушным транспортом',
        'Перевезено грузов автомобильным  и городским  электрическим транспортом': 'перевезено грузов автомобильным  и городским  электрическим транспортом',
        'не состоит в зарегистрированном браке': 'не состоял (а) в браке',
        'Не состоял (а) в браке': 'не состоял (а) в браке',
        'брак зарегистрирован': 'состоял (а) в браке',
        'Состоял (а) в браке': 'состоял (а) в браке',
        'Не указано': 'не указано',
        'Разведен(а)': 'разведен(а)',
        'Вдовец (вдова)': 'вдовец (вдова)',
        'Обеспеченность врачами (без зубных)': 'Обеспеченность врачами на \
1 000 населения (без зубных)',
        'Обеспеченность средними медицинскими работниками': 'Обеспеченность средними медицинскими работниками на 1 000 населения',
        'Обеспеченность стоматологами (включая зубных техников)': 'Обеспеченность стоматологами на 1 000 населения (включая зубных техников)',
        'Обеспеченность фармацевтическими работниками (включая провизоров)': 'Обеспеченность фармацевтическими работниками на 1 000 населения (включая провизоров)',
        'выше 10 Мбит/сек': 'выше 10 Мбит/сек',
        'жещины': 'женщины',
        'Доля женщинв возрасте 20-24 года, вступивших в брак до наступления полных 18 лет': 'Доля женщин в возрасте 20-24 года, вступивших в брак до наступления полных 18 лет',
    }
    if disagg in disagg_fixes:
        return disagg_fixes[disagg]
    return disagg

# Should we skip this row?
def skip_disaggregation_row(disagg):
    disagg_skip = [
        #'всего',
        #'Всего'
    ]
    return disagg in disagg_skip

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
    indicator = 'indicator_' + id.replace('.', '-') + '.csv'

    csv_filename = indicator

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
    # Some cleanup.
    if ret == 'г':
        ret = False
    # If False, return that now.
    if ret == False:
        return False
    # Number of parts.
    parts = ret.split('.')
    num_parts = len(parts)
    # Require at least three parts.
    if num_parts < 3:
        return False
    # Require less than 5 parts.
    if num_parts > 4:
        return False

    # If the last part is longer than 1 character and starts with a number,
    # assume it should just be the number.
    last_part = num_parts - 1
    if len(parts[last_part]) > 1 and parts[last_part][0].isdigit():
        parts[last_part] = parts[last_part][0]

    # Finally join the parts and return it.
    ret = '.'.join(parts)

    # Debugging - is this somehow returning non-Latin characters?
    if not isLatin(ret):
        print('WARNING: Non-latin charcters in indicator id: ' + ret)

    return ret

# Create a dict representing one row in ultimate CSV file.
def get_csv_row(year, disaggregations, value, unit):
    global units
    # Save the units for later.
    if unit:
        units[unit] = True
    ret = {}
    ret[HEADER_YEAR] = year
    ret[HEADER_UNIT] = unit
    for disaggregation in disaggregations:
        ret[disaggregation] = disaggregations[disaggregation]
    ret[HEADER_VALUE] = value
    return ret

# Read the excel file.
def read_excel(sheet):
    # Read the Excel spreadsheet into a dataframe.
    excel_opts = {
        'sheet_name': sheet,
        'header': None,
        'names': ['id','global','national','unit'] + YEARS + METADATA,
        'skiprows': [0,1,2,3,4],
        'usecols': [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    }
    df = pd.read_excel('scripts/batch/data.xls', **excel_opts)
    return df

# Read the disaggregation info spreadsheet.
def read_disaggregations():
    # Read the Excel spreadsheet into a dataframe.
    excel_opts = {
        'header': None,
        'names': ['value', 'category'],
        'skiprows': [0],
        'usecols': [0,4]
    }
    df = pd.read_excel('scripts/batch/disaggregations.xls', **excel_opts)
    # We only care if both category and value are there.
    df = df.dropna()
    # Make sure everything is a string.
    df = df.applymap(str)
    return df

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

# Is this indicator national or global?
def get_national_or_global(row):
    # Indicators can have global and/or national names. Prefer national.
    if not pd.isna(row['national']):
        return 'national'
    if not pd.isna(row['global']):
        return 'global'
    # Otherwise this is not an indicator start row.
    return False

# Get the name of an indicator.
def get_indicator_name(row, national_or_global, indicator_id):
    name = row[national_or_global]
    name = name.replace(indicator_id, '')
    return name.strip()

# Is this row the beginning of an indicator? If so, return the indicator id.
def is_indicator_start(row):
    # At this point we don't know yet whether this is global or national. So
    # we have to look in both columns. We prefer national.
    if pd.isna(row['global']) and pd.isna(row['national']) and pd.isna(row['id']):
        return False
    else:
        # First look in a dedicated column for it.
        id = indicator_id(row['id'])
        if not id:
            id = indicator_id(row['national'])
        if not id:
            id = indicator_id(row['global'])
        if id:
            return id
        else:
            return False

# Is this row the beginning of a disaggregation category? If so, return that
# category.
def is_disaggregation_start(row, indicator_id):
    # Disaggregation categories never have yearly data.
    if has_yearly_data(row):
        return False
    # Disaggregation categories should not have any metadata. (Though some do,
    # so commenting this out.)
    #if has_metadata(row):
    #    return False
    # Disaggregation categories will either be under 'global' or 'national'.
    national_or_global = indicator_map[indicator_id]['national_or_global']
    disaggregation = row[national_or_global]
    # But sometimes it is in the other column...
    if pd.isnull(disaggregation):
        other_column = 'national' if national_or_global == 'global' else 'global'
        disaggregation = row[other_column]
    if pd.isnull(disaggregation):
        return False
    # Finally check against our disaggregations table. If we don't know about
    # this one, ignore it.
    if isinstance(disaggregation, str):
        disaggregation = disaggregation.strip()
    # Fix disaggregations.
    disaggregation = fix_disaggregation(disaggregation)
    if not is_valid_disaggregation(disaggregation):
        return False
    return disaggregation

def isLatin(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

# Does this row have any metadata?
def has_metadata(row):
    if row[METADATA].isnull().all():
        return False
    return True

# Is this row a set of yearly data?
def has_yearly_data(row):
    if row[YEARS].isnull().all():
        return False
    return True

# Convert the indicator id into a goal id.
def get_indicator_goal(id):
    return id.split('.')[0]

# Convert the indicator id into a target id.
def get_indicator_target(id):
    parts = id.split('.')
    return parts[0] + '.' + parts[1]

# Is there any source information?
def has_source_info(row):
    if pd.isna(row['implementation']) and pd.isna(row['compilation']) and pd.isna(row['source']):
        return False
    return True

# Convert an indicator id into a translation key.
def get_translation_key(indicator_id):
    return 'name-' + indicator_id.replace('.', '-')

# Clean up rows of data.
def clean_row(row):
    # TODO: Remove non-numeric values from year columns.
    remove = ['...','(',')','*','…','-']
    convert = {',': '.'}
    for year in YEARS:
        if not pd.isnull(row[year]):
            if isinstance(row[year], str):
                val = row[year]
                for item in remove:
                    val = val.replace(item, '')
                for find in convert:
                    val = val.replace(find, convert[find])
                val = val.strip()
                # If we are left with an empty string, change to null.
                if val == '':
                    val = None
                # Finally convert numbers to actual numbers.
                if val != None:
                    converted_val = val
                    # Floats.
                    try:
                        converted_val = float(val)
                        val = converted_val
                    except ValueError:
                        pass
                    try:
                        converted_val = int(val)
                        val = converted_val
                    except:
                        pass
                # At this point, if it is still a string, kill it.
                if isinstance(val, str):
                    val = None
                row[year] = val
    return row

# Create rough data structure from an Excel sheet.
def parse_excel_sheet(sheet):
    global indicator_map
    global disagg_mismatches_with_data
    global DEBUG
    df = read_excel(sheet)
    # Figure out where each indicator starts and set the ID.
    current_id = False
    current_disaggregations = []
    last_unit = ''
    found_all_disaggregations = False
    round_these_columns = ['customisation','classification','availability']
    fix_empty_values = ['source','unit','availability','customisation','classification','implementation','compilation']
    for index, row in df.iterrows():

        # Clean up rows.
        row = clean_row(row)

        # Skip blank rows.
        if row.isnull().all():
            continue

        #alert('Parsing new row')

        # Is this the beginning of an indicator?
        indicator_start = is_indicator_start(row)
        if indicator_start:
            alert('Start of indicator: ' + indicator_start)
            # Round some columns by converting them to ints.
            for column in round_these_columns:
                if isinstance(row[column], float) and not pd.isnull(row[column]):
                    row[column] = int(row[column])
            # Fix empty values in these columns.
            for column in fix_empty_values:
                if pd.isnull(row[column]):
                    row[column] = None
                elif isinstance(row[column], str):
                    row[column] = row[column].strip()

            current_id = indicator_start
            if DEBUG_INDICATOR:
                DEBUG = current_id == DEBUG_INDICATOR
            # Reset some disaggregation-related variables.
            current_disaggregations = []
            if (not pd.isnull(row['unit'])) and row['unit'] != '':
                #alert('initializing unit to ' + row['unit'])
                last_unit = row['unit'].strip()
            found_all_disaggregations = False
            # Is this is in the national or global column?
            national_or_global = get_national_or_global(row)
            # Not already there, initialize the data about this one.
            if current_id not in indicator_map:
                name_translation_key = get_translation_key(current_id)
                name_translation = 'meta.' + name_translation_key
                name = get_indicator_name(row, national_or_global, current_id)
                # Output some text to copy into a translation file. This has
                # been done once, so no need to output this anymore.
                #print(name_translation_key + ': ' + name)
                #tags = []
                # Give it a tag if the customisation value is more than 1.
                #if isinstance(row['customisation'], int) and row['customisation'] > 1:
                #    tag = 'meta.customisation-' + str(row['customisation'])
                #    tags.append(tag)
                indicator_map[current_id] = {
                    'national_or_global': national_or_global,
                    'meta': {
                        'indicator': current_id,
                        'sdg_goal': get_indicator_goal(current_id),
                        'target_id': get_indicator_target(current_id),
                        'indicator_name': name_translation,
                        'graph_title': name_translation,
                        'indicator_sort_order': get_indicator_sort_order(current_id),
                        'source_active_1': has_source_info(row),
                        'source_data_1': row['source'],
                        'source_compilation_1': row['compilation'],
                        'source_implementation_1': row['implementation'],
                        #'customisation': row['customisation'],
                        #'classification': row['classification'],
                        #'availability': row['availability'],
                        'computation_units': last_unit,
                        'tags': []
                    },
                    'data': []
                }
                # Set the reporting status according to the presence of data.
                if not has_yearly_data(row):
                    indicator_map[current_id]['meta']['reporting_status'] = 'notstarted'
                else:
                    indicator_map[current_id]['meta']['reporting_status'] = 'complete'


            # In some cases, there is data in the starting row. We assume
            # in these cases that there is no disaggregation.
            if has_yearly_data(row):
                alert('Data was in starting row: ' + current_id)
                data = {
                    'disaggregations': [],
                    'years': row[YEARS],
                    'unit': last_unit
                }
                indicator_map[current_id]['data'].append(data)

        # Otherwise, is this more data for an indicator?
        elif current_id:
            if DEBUG_INDICATOR:
                DEBUG = current_id == DEBUG_INDICATOR
            # First look up some info about this indicator.
            national_or_global = indicator_map[current_id]['national_or_global']
            # Update the unit if necessary
            if (not pd.isnull(row['unit'])) and row['unit'] != '':
                #alert('updating unit to ' + str(row['unit']))
                last_unit = row['unit'].strip()
            # Does this row indicate a disaggregation category?
            disagg_start = is_disaggregation_start(row, current_id)
            if disagg_start:
                #alert('Disaggregation start: ' + disagg_start)
                # If we had previous found all categories (in other words,
                # we encountered a value after finding some categories) then
                # we start a new list here.
                if found_all_disaggregations:
                    #alert('Had previously found all disaggregations')
                    current_disaggregations = [disagg_start]
                    found_all_disaggregations = False
                # Otherwise, we append to the current list.
                else:
                    current_disaggregations.append(disagg_start)

                #alert('Continuing to next row')
                continue

            # If we get to this point we assume everything is yearly data.
            # If there is no yearly data, we won't know how to understand
            # what this row is.
            if not has_yearly_data(row):
                #alert('Assuming end of current disaggregations')
                # We have to assume that this means that any current
                # disaggregations have ended, so reset the disagg stuff.
                current_disaggregations = []
                found_all_disaggregations = False
                continue

            # Now we are looking at a row with values. This means that all
            # the disaggregation categories have been found.
            found_all_disaggregations = True
            row_disaggregation = current_disaggregations.copy()
            # Might this row include a disaggregation?
            potential_disagg_row = row[national_or_global]
            if pd.isnull(potential_disagg_row):
                # Sometimes the disaggregation is in the wrong column...
                other_column = 'national' if national_or_global == 'global' else 'global'
                potential_disagg_row = row[other_column]
            if not pd.isnull(potential_disagg_row):
                # Add this disaggregation, if any.
                disagg_value = potential_disagg_row
                # Strip whitespace if it is a string.
                if isinstance(disagg_value, str):
                    disagg_value = disagg_value.strip()
                # Fix disagg discrepancies.
                disagg_value = fix_disaggregation(disagg_value)
                # Skip certain disaggregations.
                if skip_disaggregation_row(disagg_value):
                    continue
                # Otherwise add the disagg if it is valid.
                if is_valid_disaggregation(disagg_value):
                    row_disaggregation.append(disagg_value)
                else:
                    # If it was not valid, and the row contains yearly data,
                    # then we should take note, as it is probably a problem.
                    if has_yearly_data(row):
                        if disagg_value not in disagg_mismatches_with_data:
                            disagg_mismatches_with_data[disagg_value] = {}
                        disagg_mismatches_with_data[disagg_value][current_id] = True
                        # For now we will have to skip the entire row.
                        #continue

            data = {
                'disaggregations': row_disaggregation,
                'years': row[YEARS],
                'unit': last_unit
            }
            alert('Adding a row of data with disaggregations: ' + ', '.join(row_disaggregation))
            indicator_map[current_id]['data'].append(data)
        else:
            alert('uhoh')

# Check a string is a valid disaggregation.
def is_valid_disaggregation(disagg):
    global disagg_mismatches
    global single_disagg_values
    global disagg_matches
    #alert('Testing disaggregation for validity: "' + disagg + '"')
    if disagg is None or not disagg:
        return False
    if disagg in single_disagg_values:
        alert('Invalid disaggregation because it is a single-category value: ' + disagg)
        return False
    if disagg not in disagg_table:
        # Save this for a report of database/disaggregation mismatch.
        disagg_string = disagg
        if not isinstance(disagg_string, str):
            disagg_string = str(disagg_string)
        disagg_mismatches[disagg_string] = True
        alert('Invalid disaggregation because it is not in the map: ' + disagg_string)
        return False
    #alert('Valid!')
    disagg_matches[disagg_table[disagg]] = True
    disagg_matches[disagg] = True
    return True

# Convert list of disaggregations into a category:value structure.
def build_disaggregation_dict(disagg_list):
    disagg_dict = {}
    for disagg in disagg_list:
        category = disagg_table[disagg]
        disagg_dict[category] = disagg
    return disagg_dict

# Output the metadata.
def output_meta(indicator_id):
    # First some defaults for indicators that don't exist yet.
    defaults = {
        'data_non_statistical': False,
        'graph_type': 'line',
    }
    required = {
        'published': True,
        'reporting_status': 'complete',
        'national_geographical_coverage': 'Казахстан',
    }
    # Get the existing metadata, if any.
    filename = indicator_id.replace('.', '-') + '.md'
    filepath = os.path.join(FOLDER_METADATA_YAML, filename)
    metadata = defaults.copy()
    if os.path.isfile(filepath):
        metadata = get_metadata(filepath)

    metadata.update(required)
    metadata.update(indicator_map[indicator_id]['meta'])

    yaml_string = yaml.dump(metadata,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=True,
        allow_unicode=True)
    with open(filepath, 'w') as outfile:
        outfile.write(yaml_string.replace("\n...\n", "\n---\n"))

    #write_indicator_for_site_repo(metadata)

# Output data.
def output_data(indicator_id):
    indicator_info = indicator_map[indicator_id]
    csv_rows = []
    all_disaggregations = []
    for series in indicator_info['data']:
        disaggs = build_disaggregation_dict(series['disaggregations'])
        for category in disaggs:
            if (category not in all_disaggregations):
                all_disaggregations.append(category)
        for year, value in series['years'].iteritems():
            # Filter out some invalid data.
            if not year.isdigit():
                continue
            if pd.isnull(value):
                continue
            if isinstance(value, str):
                continue
            csv_row = get_csv_row(year, disaggs, value, series['unit'])
            csv_rows.append(csv_row)

    csv_df = blank_dataframe(all_disaggregations)
    for row in csv_rows:
        csv_df = csv_df.append(row, ignore_index=True)

    if not csv_df.empty:
        write_csv(indicator_id, csv_df)

# Process indicator.
def process_indicator(indicator_id):
    foo = 'bar'
    output_data(indicator_id)
    #output_meta(indicator_id)

# Main function.
def main():
    """Tidy up all of the indicator CSVs in the data folder."""

    global disagg_table
    global single_disagg_values
    global disagg_matches
    global disagg_mismatches_with_data
    global units
    status = True

    # Read the disaggregation table.
    disaggs = read_disaggregations()
    disaggs['value'] = disaggs['value'].str.strip()
    disaggs['category'] = disaggs['category'].str.strip()
    disagg_table = dict(zip(disaggs.value, disaggs.category))

    # Note disaggregations from the table that have only 1 value per category.
    disaggs_by_category = {}
    for disagg in disagg_table:
        category = disagg_table[disagg]
        if category not in disaggs_by_category:
            disaggs_by_category[category] = [disagg]
        elif disagg not in disaggs_by_category[category]:
            disaggs_by_category[category].append(disagg)

    single_disagg_categories = []
    single_disagg_values = []
    for category in disaggs_by_category:
        if len(disaggs_by_category[category]) == 1:
            single_disagg_categories.append(category)
            single_disagg_values.append(disaggs_by_category[category][0])

    # Sheets in the Excel file.
    #sheets = ['SDG 4']
    sheets = ['SDG 1','SDG 2','SDG 3','SDG 4','SDG 5','SDG 6','SDG 7','SDG 8','SDG 9','SDG 10','SDG 11','SDG 12','SDG 13','SDG 14','SDG 15','SDG 16','SDG 17']
    #sheets = ['SDG 1','SDG 2','SDG 3','SDG 4','SDG 5','SDG 6', 'SDG 7']

    # Get the source data, one sheet at a time.
    for sheet in sheets:
        parse_excel_sheet(sheet)
        # Just one sheet for now.

    # Now we have rough data, and need to clean/fix it.
    for indicator_id in indicator_map:
        process_indicator(indicator_id)

    # Output the mismatches.
    #for mismatch in sorted(disagg_mismatches.keys()):
    #    print("'" + mismatch + "'")
    # Output the matches.
    #for match in disagg_matches.keys():
    #    print(match)
    # Output the units.
    #for unit in units.keys():
    #    print(unit)
    # Output the mismatches that had yearly data.
    #for key in disagg_mismatches_with_data:
    #    print('"' + str(key) + '", "' + ' '.join(disagg_mismatches_with_data[key].keys()) + '"')

    return status

if __name__ == '__main__':
    if not main():
        raise RuntimeError("Failed tidy conversion")
    else:
        print("Success")