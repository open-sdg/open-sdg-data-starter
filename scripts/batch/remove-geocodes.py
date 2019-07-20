import sdg
import os
import pandas as pd
import numpy as np

def filter_map_headline(df):
    """Given a dataframe filter it down to just the headline data.

    In the case of multiple units arbitrarily keep the first one.
    """

    # The pandas version on trusty doesn't support 'errors' argument so:
    if 'Units' in df.columns:
        special_cols = ['Year', 'Units', 'Регионы', 'GeoCode', 'Value']
    else:
        special_cols = ['Year', 'Регионы', 'GeoCode', 'Value']

    # Select the non-data rows and filter rows that are all missing (nan)
    disag = df.drop(special_cols, axis=1)
    headline_rows = disag.isnull().all(axis=1)

    headline = df.filter(special_cols, axis=1)[headline_rows]

    # Also make sure regions are there.
    headline = headline.dropna(subset=['Регионы'])

    if len(headline) == 0:
        return headline

    if 'Units' in headline.columns:
        unit = headline['Units'].iloc[0]
        headline = headline[headline['Units'] == unit]

    return headline


ids = sdg.path.get_ids()
for inid in ids:
    df = sdg.data.get_inid_data(inid)
    if 'GeoCode' in df.columns.tolist():
        # Look for a headline.
        headline = filter_map_headline(df)
        # If there is no headline, we will remove the GeoCodes for now.
        if len(headline) == 0:
            df['GeoCode'] = np.NaN
        else:
            # Otherwise we'll remove GeoCodes for rows not in the
            # "map headline".
            do_not_map = list(set(df.index) - set(headline.index))
            df.loc[do_not_map, 'GeoCode'] = np.NaN

        csv_filename = 'indicator_' + inid.replace('.', '-') + '.csv'
        path = os.path.join('data', csv_filename)
        df.to_csv(path, index=False, encoding='utf-8')
