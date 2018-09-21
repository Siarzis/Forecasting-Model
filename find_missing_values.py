import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def find_missing_values(input_series, gen_threshold, speed_threshold, pv_threshold, attribute, min_value, max_value):

    # input_series contains historical weather data (wind speed/wind direction, etc)
    df = input_series.to_frame()  # turn series to frame to facilitate processing
    df.columns = [attribute[1]]  # rename column; problem in transition from series to df

    # complex, one-line commands that do all the work. Unfortunately this is the way pandas do the job
    # found after search on StackOverflow
    # 'block' term is introduced in order to distinguish the different intervals in which
    # the same value can be continuously repeated
    df['block'] = (df[attribute[1]].shift(1) != df[attribute[1]]).astype(int).cumsum()
    # consecutive_intervals is a pandas Series that contain all intervals of interest
    consecutive_intervals = df.reset_index().groupby([attribute[1], 'block'])['index'].apply(np.array)

    # keep a copy of original Series to plot both original and updated versions
    df_copy = df.copy()
    initial_time_series = pd.Series(df_copy[attribute[1]].values, index=df.index)

    # consecutive_intervals variables break into tuple and list with proper values
    # for iteration and accessing reasons
    for value_block_tuple, indexes in consecutive_intervals.items():  # TODO optimize if-statements
        indexes = indexes.tolist()  # turn array to list
        # below if-statements are used to cover every case of wrong measurements based on weather elements
        if pv_threshold != float('inf'):
            # in pv case value needs to be over 0.5 because of night
            if len(indexes) > gen_threshold and value_block_tuple[0] > 0.5:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')
            # pv can have close to zero values for at least 12 hours because of night
            elif len(indexes) > pv_threshold and value_block_tuple[0] <= 0.5:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')
            elif value_block_tuple[0] < min_value:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')
            elif value_block_tuple[0] > max_value:
                for elem in indexes:
                    df.at[elem, attribute[1]] = max_value
        elif speed_threshold != float('inf'):
            # in speed case zero-valued intervals are estimated in future if-statements
            if len(indexes) > gen_threshold and value_block_tuple[0] != 0:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')
            # speed my have the same value for 10 hours
            elif len(indexes) > speed_threshold and value_block_tuple[0] == 0:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')
            elif value_block_tuple[0] < min_value or value_block_tuple[0] > max_value:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')
        else:
            # general threshold that appears in all cases
            if len(indexes) > gen_threshold:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')
            elif value_block_tuple[0] < min_value or value_block_tuple[0] > max_value:
                for elem in indexes:
                    df.at[elem, attribute[1]] = float('nan')

    time_series = pd.Series(df[attribute[1]].values, index=df.index)  # turn df into series; mainly get the output

    initial_time_series.plot()
    time_series.plot()
    plt.suptitle(attribute[1] + str(attribute[0]), fontsize=16)
    plt.show()

    if pv_threshold != float('inf'):
        filename = 'Fixed PV Info/' + attribute[1] + '.csv'
    else:
        filename = 'Fixed Wind Info/' + attribute[1] + str(attribute[0]) + '.csv'
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
    df.drop(columns=['block'], inplace=True)  # delete unnecessary columns
    df.to_csv(filename, index=False)


for k in range(0, 5):
    farm_data = pd.read_csv('Wind Info\WindFarm' + str(k+1) + '.csv')
    direction_time_series = pd.Series(farm_data['WindDirection'].values, index=farm_data.index)
    find_missing_values(direction_time_series, 4, float('inf'), float('inf'), [k+1, 'WindDirection'], 0, 360)
    speed_time_series = pd.Series(farm_data['WindSpeed'].values, index=farm_data.index)
    find_missing_values(speed_time_series, 4, 10, float('inf'), [k+1, 'WindSpeed'], 0, 30)

p_rated = int(input('Please, enter P_rated value: '))
pv_data = pd.read_csv('PV Info\PvData.csv')
pv_time_series = pd.Series(pv_data['PvPower'].values, index=pv_data.index)
find_missing_values(pv_time_series, 4, float('inf'), 12, ['', 'PvPower'], 0, p_rated)
