import sdg
import os
import yaml

"""
This is a one-time script to remove global and other unneeded metadata.
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

to_delete_from_all = [
    'permalink',
    'layout'
]

ids = sdg.path.get_ids()
for inid in ids:
    filepath = os.path.join('meta', inid + '.md')
    meta = get_metadata(filepath)
    for key in to_delete_from_all:
        if key in meta:
            del meta[key]

    # While here let's reset indicator_name and graph_title for easier
    # out-of-the-box translations.
    global_name = 'global_indicators.' + inid + '-title'
    meta['indicator_name'] = global_name
    meta['graph_title'] = global_name

    write_metadata(filepath, meta)
