import sdg
import os
import yaml

"""
This is a one-time script to set the indicator name for "national modified"
indicators.
"""

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

ids = sdg.path.get_ids()
for inid in ids:
    filepath = os.path.join('meta', inid + '.md')
    meta = get_metadata(filepath)
    customisations = ['meta.customisation-3', 'meta.customisation-4']

    # We are only interested in the 3-digit indicators.
    if len(inid.split('-')) < 4 and 'customisation' in meta and meta['customisation'] in customisations:
        meta['indicator_name_national'] = 'national_indicators.' + inid + '.title'
        meta['graph_title'] = meta['indicator_name_national']
        print(inid)
    # Write the changes to disk.
    write_metadata(filepath, meta)
