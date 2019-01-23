"""
This script adds a new indicator to this implementation of Open SDG.

Usage example: the following would add 1.1.z, called "My indicator name",
as a new indicator:
    python scripts/batch/add_indicator.py 1.1.z "My indicator name"

What this script actually does:
1. This script creates a file in the meta/ folder, with sample data.
1. This script creates a file in the data/ folder, with basic metadata.

What this script does NOT do:
1. This script does not update the site repository. Note that you can use a
   similar script specifically for the site repository.
"""
import sys
import os
import yaml

def get_sample_data():
    lines = [
        'Year,Category,Value',
        '2015,,1',
        '2016,,2',
        '2017,,3',
        '2015,A,2',
        '2016,A,3',
        '2017,A,4',
        '2015,B,3',
        '2016,B,4',
        '2017,B,5',
    ]
    return "\n".join(lines)

def get_indicator_sort_order(id):
    parts = id.split('.')
    ret = []
    for part in parts:
        if len(part) < 2:
            part = '0' + part
        ret.append(part)
    return '-'.join(ret)

def get_metadata(id, name):
    parts = id.split('.')
    return {
        'data_non_statistical': False,
        'graph_type': 'line',
        'published': True,
        'reporting_status': 'complete',
        'indicator_name': name,
        'graph_title': name,
        'indicator': id,
        'indicator_sort_order': get_indicator_sort_order(id),
        'sdg_goal': parts[0],
        'target_id': parts[0] + '.' + parts[1]
    }

def add_indicator(id, name):
    # First write the metadata file.
    filename = id.replace('.', '-') + '.md'
    filepath = os.path.join('meta', filename)
    metadata = get_metadata(id, name)
    yaml_string = yaml.dump(metadata,
        default_flow_style=False,
        explicit_start=True,
        explicit_end=True)
    with open(filepath, 'w') as outfile:
        outfile.write(yaml_string.replace("\n...\n", "\n---\n"))

    # Now write the data.
    filename = 'indicator_' + id.replace('.', '-') + '.csv'
    filepath = os.path.join('data', filename)
    data = get_sample_data()
    f = open(filepath, 'w')
    f.write(data)
    f.close()

def main():

    # Abort if there is no parameter provided.
    if len(sys.argv) < 3:
        sys.exit('Provide the id number and name of this indicator.')
    id = sys.argv[1]
    name = sys.argv[2]
    add_indicator(id, name)
    print("Remember to update and deploy this change before proceeding to the similar script in the site repository.")

# Boilerplace syntax for running the main function.
if __name__ == '__main__':
    main()
