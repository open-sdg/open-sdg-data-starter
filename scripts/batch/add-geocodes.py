import sdg
import os
import pandas as pd

geocodes = {
    "Регионы": "Regions",
    "Акмолинская": "KZ03",
    "Актюбинская": "KZ04",
    "Алматинская": "KZ01",
    "Атырауская": "KZ06",
    "Западно-Казахстанская": "KZ07",
    "Жамбылская": "KZ17",
    "Карагандинская": "KZ12",
    "Костанайская": "KZ13",
    "Кызылординская": "KZ14",
    "Мангистауская": "KZ09",
    "Южно-Казахстанская": "KZ10",
    "Павлодарская": "KZ11",
    "Северо-Казахстанская": "KZ16",
    "Туркестанская": "KZ10",
    "Восточно-Казахстанская": "KZ15",
    "г.Нур-Султан": "KZ05",
    "г.Алматы": "KZ02",
    "г.Шымкент": "KZ18"
}
# TODO: Confirm whether duplicates for KZ10 are correct.

ids = sdg.path.get_ids()
for inid in ids:
    df = sdg.data.get_inid_data(inid)
    if 'Регионы' in df.columns.tolist():
        df['GeoCode'] = df['Регионы'].map(geocodes)
        cols = df.columns.tolist()
        cols.pop(cols.index('Year'))
        cols.pop(cols.index('Value'))
        cols = ['Year'] + cols + ['Value']
        df = df[cols]

        csv_filename = 'indicator_' + inid.replace('.', '-') + '.csv'
        path = os.path.join('data', csv_filename)
        df.to_csv(path, index=False, encoding='utf-8')
