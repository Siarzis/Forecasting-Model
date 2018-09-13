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

for i, v in consecutive_pv_intervals.items():
    v = v.tolist()  # turn array to list
    # our code also prints the ids of values that appeared only once. Here we eliminate those ids
    if len(v) > 1:
        pass
        #print('Wrong PV Value:', i[0], '| Block:', i[1], '--> Interval:', v[::len(v) - 1])
        #print(v[0][0], v[0][1], v[-1][0], v[-1][1])
