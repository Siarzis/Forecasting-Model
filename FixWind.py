import pandas as pd
import numpy as np


def fix_wind_measurements():
    farm_id = [0, 1, 2, 3, 4]  # contains all farm ids
    chosen_farms = []  # list with chosen farms ids
    farms_data = []  # a list of each farm's DataFrame

    # choose a wind farm and keep the rest
    rest_farms = [x for x in farm_id if x not in chosen_farms]

    # turn csv into pandas DataFrame and add it to farms_data list
    # range is between 1 and 6 because of the .csv files' names
    for i in range(1, 6):
        farms_data.append(pd.read_csv('Wind Info\WindFarm' + str(i) + '.csv'))  # turn csv into pandas DataFrame

    # complex but effective way to find indexes of NaN values in DataFrame
    nan_indexes = farms_data[1][np.isnan(farms_data[1]['Wind Speed'])].index.values.tolist()
    # nan_indexes = pd.isnull(farms_data[1]).any(1).nonzero()[0]

    # 'i' is the the id of wind speed column with NaN value
    # 'j' is the number of wind farm
    for i in nan_indexes:
        inp = []
        index = [0, 0, 0, 0, 0]
        for j in rest_farms:
            wind_speed = farms_data[j]['Wind Speed'].iloc[i]  # find farm's wind speed by position
            if not np.isnan(wind_speed):
                inp.append(wind_speed)
                index[j] = 1
        if sum(index) > 0:
            pass

    print(farms_data[0]['Wind Speed'].iloc[3])


fix_wind_measurements()
