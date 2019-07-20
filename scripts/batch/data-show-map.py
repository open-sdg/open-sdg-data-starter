import sdg
import os
import yaml

"""
This is a one-time script to update the "data_show_map" of all
indicators according to whether they have GeoCode.
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
    # Load the raw
    data = sdg.data.get_inid_data(inid)
    cols = data.columns
    filepath = os.path.join('meta', inid + '.md')
    meta = get_metadata(filepath)
    if 'GeoCode' in cols and data['GeoCode'].any():
        meta['data_show_map'] = True
    else:
        meta['data_show_map'] = False
    write_metadata(filepath, meta)