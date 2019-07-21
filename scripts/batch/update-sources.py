# -*- coding: utf-8 -*-
"""
This script imports existing data for Kazakhstan from an Excel file.
"""

import glob
import os.path
import yaml
import sdg

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

def already_updated(meta):
    updated = False
    if 'source_data_1' in meta and meta['source_data_1'] != '' and meta['source_data_1'] is not None:
        if isinstance(meta['source_data_1'], str) and meta['source_data_1'].startswith('sources.'):
            updated = True
    if 'source_implementation_1' in meta and meta['source_implementation_1'] != '' and meta['source_implementation_1'] is not None:
        if isinstance(meta['source_implementation_1'], str) and meta['source_implementation_1'].startswith('sources.'):
            updated = True
    if 'source_compilation_1' in meta and meta['source_compilation_1'] != '' and meta['source_compilation_1'] is not None:
        if isinstance(meta['source_compilation_1'], str) and meta['source_compilation_1'].startswith('sources.'):
            updated = True
    return updated

translation_yaml = {}

ids = sdg.path.get_ids()
for inid in ids:
    filepath = os.path.join('meta', inid + '.md')
    meta = get_metadata(filepath)
    if 'source_active_1' in meta and meta['source_active_1'] == True:
        if not already_updated(meta):
            indicator_sources = {}
            if 'source_data_1' in meta and meta['source_data_1'] != '' and meta['source_data_1'] is not None:
                if isinstance(meta['source_data_1'], str):
                    indicator_sources['source_data_1'] = meta['source_data_1']
                    meta['source_data_1'] = 'sources.' + inid + '.source_data_1'
            if 'source_implementation_1' in meta and meta['source_implementation_1'] != '' and meta['source_implementation_1'] is not None:
                if isinstance(meta['source_implementation_1'], str):
                    indicator_sources['source_implementation_1'] = meta['source_implementation_1']
                    meta['source_implementation_1'] = 'sources.' + inid + '.source_implementation_1'
            if 'source_compilation_1' in meta and meta['source_compilation_1'] != '' and meta['source_compilation_1'] is not None:
                if isinstance(meta['source_compilation_1'], str):
                    indicator_sources['source_compilation_1'] = meta['source_compilation_1']
                    meta['source_compilation_1'] = 'sources.' + inid + '.source_compilation_1'

            translation_yaml[inid] = indicator_sources
            write_metadata(filepath, meta)

write_metadata('sources.yml', translation_yaml)