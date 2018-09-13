# ------------------------------------------------------------------------------------
# --- temporary file that is used to convert a .mat file to proper .csv (manually) ---
# -------------------------------- IT WORKS ------------------------------------------
# ------------------------------------------------------------------------------------

import scipy.io
import numpy as np
import csv
import os

# mat is a dict data structure
# load .mat file to variable
mat = scipy.io.loadmat('Wind_info.mat')

mat = mat['info']

# this variable is introduced to facilitate the creation of .csv files
# it allows us to choose the id of wind farm
farm_id = 0

sample_table = [[], [], [], []]

# some 'patentes' to index the right elements from the complex .mat file.
# import dates
for x in mat[0][0][0]:
    sample_table[0].append(x[0][0])


# import setpoints
for x in np.nditer(mat[0][farm_id][1]):
    sample_table[1].append(x)

# import wind speed
for x in np.nditer(mat[0][farm_id][2]):
    sample_table[2].append(x)

# import wind direction
for x in np.nditer(mat[0][farm_id][3]):
    sample_table[3].append(x)

filename = 'Wind Info\WindFarm' + str(farm_id+1) + '.csv'

# checks if the 'WindFarm1.csv' file is already created to prevent overwriting (and extending)
# the same file again and again. It is used for our own convenience
if os.path.exists(filename):
    try:
        os.remove(filename)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

with open(filename, 'w', newline='') as csvfile:
    wr = csv.writer(csvfile)
    wr.writerow(['Dates', 'SetPoints', 'Wind Speed', 'Wind Direction'])
    for j in range(0, len(sample_table[0])):
        wr.writerow([sample_table[0][j], sample_table[1][j], sample_table[2][j], sample_table[3][j]])
