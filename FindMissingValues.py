# ------------------------------------------------------------------------------------------------
# we track .csv 's  ids of consecutively same values because it indicates problems in measurements
# ------------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import os

# --------------------------------------------  Wind Data Fix  ------------------------------------------------------

for k in range(0, 5):
    farm_id = pd.read_csv('Wind Info\WindFarm' + str(k+1) + '.csv')

    # complex, one-line commands that do all the work. Unfortunately this is the way pandas do the job
    # found after search on StackOverflow
    # 'block' term is introduced in order to distinguish the different intervals that
    # the same value can be continuously repeated
    farm_id['block1'] = (farm_id.WindSpeed.shift(1) != farm_id.WindSpeed).astype(int).cumsum()
    farm_id['block2'] = (farm_id.WindDirection.shift(1) != farm_id.WindDirection).astype(int).cumsum()
    # consecutive_intervals is a pandas Series that contain all intervals of interest
    consecutive_speed_intervals = farm_id.reset_index().groupby(['WindSpeed', 'block1'])['index'].apply(np.array)
    consecutive_direction_intervals = farm_id.reset_index().groupby(['WindDirection', 'block2'])['index'].apply(np.array)

    # consecutive_intervals variables break into tuple and list with proper values
    # for iteration and accessing reasons
    for speed_block_tuple, indexes in consecutive_speed_intervals.items():
        indexes = indexes.tolist()  # turn array to list
        # if measurements give the same value for 4  hours and above then they are not accepted
        if len(indexes) > 3 and speed_block_tuple[0] != 0:
            for elem in indexes:
                farm_id.at[elem, 'WindSpeed'] = float('nan')
        # contrary to previous one, if measurements are zero for 10 hours and above then they are not accepted
        # this is reasonable because no windy conditions may occur
        if len(indexes) > 9 and speed_block_tuple[0] == 0:
            for elem in indexes:
                farm_id.at[elem, 'WindSpeed'] = float('nan')

    for dir_block_tuple, indexes in consecutive_direction_intervals.items():
        indexes = indexes.tolist()  # turn array to list
        # same pattern as above
        if len(indexes) > 3:
            for elem in indexes:
                farm_id.at[elem, 'WindDirection'] = float('nan')

    filename = 'New Wind Info\WindFarm' + str(k+1) + '.csv'
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
    farm_id.to_csv(filename)

# ----------------------------------------------  PV Data Fix  ------------------------------------------------------

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
