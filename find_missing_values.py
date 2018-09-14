import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def find_missing_values(file, threshold_1, threshold_2):

    pv_threshold = float('inf')
    # file contains the path to the chosen .csv
    df = pd.read_csv(file)

    if file == 'PV Info/PvData.csv' and threshold_2 == float('inf'):
        attribute = 'PvPower'
        pv_threshold = 12
    elif file == 'PV Info/PvData.csv' and threshold_2 != float('inf'):
        print('Invalid input parameters! Please try again.')
        return
    else:
        if threshold_2 == float('inf'):  # only direction
            attribute = 'WindDirection'
        else:
            attribute = 'WindSpeed'

    # complex, one-line commands that do all the work. Unfortunately this is the way pandas do the job
    # found after search on StackOverflow
    # 'block' term is introduced in order to distinguish the different intervals in which
    # the same value can be continuously repeated
    df['block'] = (df[attribute].shift(1) != df[attribute]).astype(int).cumsum()
    # consecutive_intervals is a pandas Series that contain all intervals of interest
    consecutive_intervals = df.reset_index().groupby([attribute, 'block'])['index'].apply(np.array)

    # keep a copy of original Series to plot both original and updated versions
    initial_wind_farm = df.copy()
    initial_time_series = pd.Series(initial_wind_farm[attribute].values, index=df['Dates'])

    # consecutive_intervals variables break into tuple and list with proper values
    # for iteration and accessing reasons
    for value_block_tuple, indexes in consecutive_intervals.items():
        indexes = indexes.tolist()  # turn array to list
        # if measurements give the same value for 4  hours and above then they are not accepted
        if len(indexes) > threshold_1 and value_block_tuple[0] != 0:  # TODO check for this condition
            for elem in indexes:
                df.at[elem, attribute] = float('nan')
        # contrary to previous one, if measurements are zero for 10 hours and above, then they are not accepted
        # this is reasonable because no windy conditions may occur
        if len(indexes) > threshold_2 and value_block_tuple[0] == 0:
            for elem in indexes:
                df.at[elem, attribute] = float('nan')
        if len(indexes) > pv_threshold and value_block_tuple[0] <= 0.5:
            for elem in indexes:
                df.at[elem, attribute] = float('nan')

    time_series = pd.Series(df[attribute].values, index=df['Dates'])

    initial_time_series.plot()
    time_series.plot()
    plt.show()


while True:

    while True:
        filename = input("Please enter your file's name: ")
        if re.match(r"Wind Info/WindFarm[1-5].csv$|PV Info/PvData.csv$", filename):  # TODO regex may need modification
            break
        else:
            print("Sorry, your response does not match proper input! Please try again.")
            continue

    while True:
        try:
            parameter_1 = int(input("Please enter general parameter value: "))
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        else:
            break

    parameter_2 = float(input("Please enter wind speed parameter value: "))

    find_missing_values(filename, parameter_1, parameter_2)
