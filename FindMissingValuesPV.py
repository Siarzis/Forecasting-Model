import pandas as pd
import numpy as np

pv_data = pd.read_csv('PV Info\PvData.csv', index_col='Dates')
pv_data.columns.name = 'Hours'  # add a proper name to .csv 's columns
# --- very useful link for DataFrame reshaping https://pandas.pydata.org/pandas-docs/stable/reshaping.html ---
# we need a proper way to turn the 2D DataFrame to a 1D Series to find consecutive intervals
pv_data = pv_data.stack().to_frame()

pv_data.rename(columns={0: 'A'}, inplace=True)
pv_data['block'] = (pv_data.A.shift(1) != pv_data.A).astype(int).cumsum()
consecutive_pv_intervals = pv_data.reset_index().groupby(['A', 'block']).apply(np.array)

for pv_block_tuple, indexes in consecutive_pv_intervals.items():
    indexes = indexes.tolist()  # turn array to list
    print(indexes)
    if len(indexes) > 5 and pv_block_tuple[0] >= 0.5:
        for elem in indexes:
            pv_data.at[(elem[0], elem[1]), 'A'] = float('nan')
    if len(indexes) > 12 and pv_block_tuple[0] <= 0.5:
        for elem in indexes:
            pv_data.at[(elem[0], elem[1]), 'A'] = float('nan')
