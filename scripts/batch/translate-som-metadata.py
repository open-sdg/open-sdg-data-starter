import sdg
import os
import yaml

"""
This is a one-time script to update the "reporting_status" of all
indicators according to whether they have data.
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

foo = {}

ids = sdg.path.get_ids()
for inid in ids:
    filepath = os.path.join('meta', inid + '.md')
    meta = get_metadata(filepath)
    #if 'national_geographical_coverage' in meta:
    #    meta['national_geographical_coverage'] = 'meta.Казахстан'
    if 'computation_units' in meta and meta['computation_units']:
      units = meta['computation_units']
      meta['computation_units'] = 'data.' + units
    write_metadata(filepath, meta)

for key in foo:
  print(key)