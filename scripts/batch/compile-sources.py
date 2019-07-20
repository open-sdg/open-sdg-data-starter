import sdg
import os
import yaml

source_data = {}

# Get the metadata for an indicator.
def get_metadata(filepath):
    with open(filepath, 'r') as stream:
        try:
            for doc in yaml.safe_load_all(stream):
                if hasattr(doc, 'items'):
                    return doc
        except yaml.YAMLError as e:
            print(e)

ids = sdg.path.get_ids()
for inid in ids:
    filepath = os.path.join('meta', inid + '.md')
    meta = get_metadata(filepath)
    if 'source_compilation_1' in meta:
        source_data[meta['source_compilation_1']] = True
    if 'source_data_1' in meta:
        source_data[meta['source_data_1']] = True
    if 'source_implementation_1' in meta:
        source_data[meta['source_implementation_1']] = True

for key in source_data:
    if isinstance(key, str):
        print('"' + key + '"')
