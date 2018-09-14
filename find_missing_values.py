import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def find_missing_values(file, threshold_1, threshold_2):

    # file contains the path to the chosen .csv
    wind_farm = pd.read_csv(file)

    if threshold_2 == float('Inf'):
        attribute = 'WindDirection'
    else:
        attribute = 'WindSpeed'

    # complex, one-line commands that do all the work. Unfortunately this is the way pandas do the job
    # found after search on StackOverflow
    # 'block' term is introduced in order to distinguish the different intervals in which
    # the same value can be continuously repeated
    wind_farm['block'] = (wind_farm[attribute].shift(1) != wind_farm.WindSpeed).astype(int).cumsum()
    # consecutive_intervals is a pandas Series that contain all intervals of interest
    consecutive_intervals = wind_farm.reset_index().groupby([attribute, 'block'])['index'].apply(np.array)

    # keep a copy of original Series to plot both original and updated versions
    initial_wind_farm = wind_farm.copy()
    initial_wind_time_series = pd.Series(initial_wind_farm[attribute].values, index=wind_farm['Dates'])

    # consecutive_intervals variables break into tuple and list with proper values
    # for iteration and accessing reasons
    for value_block_tuple, indexes in consecutive_intervals.items():
        indexes = indexes.tolist()  # turn array to list
        # if measurements give the same value for 4  hours and above then they are not accepted
        if len(indexes) > threshold_1 and value_block_tuple[0] != 0:  # TODO check for this condition
            for elem in indexes:
                wind_farm.at[elem, attribute] = float('nan')
        # contrary to previous one, if measurements are zero for 10 hours and above, then they are not accepted
        # this is reasonable because no windy conditions may occur
        if len(indexes) > threshold_2 and value_block_tuple[0] == 0:
            for elem in indexes:
                wind_farm.at[elem, attribute] = float('nan')

    wind_time_series = pd.Series(wind_farm[attribute].values, index=wind_farm['Dates'])

    initial_wind_time_series.plot()
    wind_time_series.plot()
    plt.show()


while True:

    while True:
        filename = input("Please enter your file's name: ")
        if re.match(r"Wind Info/WindFarm[1-5].csv$|PvData.csv$", filename):  # TODO regex may need modification
            break
        else:
            print("Sorry, your response does not match proper input! Please try again.")
            continue

    while True:
        try:
            parameter_1 = int(input("Please enter 1st wind parameter name: "))
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        else:
            # age was successfully parsed!
            # we're ready to exit the loop.
            break

    while True:
        try:
            parameter_2 = int(input("Please enter 2nd wind parameter name: "))
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        else:
            # age was successfully parsed!
            # we're ready to exit the loop.
            break

    find_missing_values(filename, parameter_1, parameter_2)
