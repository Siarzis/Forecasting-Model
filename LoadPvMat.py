import scipy.io
import os
import csv

# mat is a dict data structure
# load .mat file to variable
mat = scipy.io.loadmat('pv_data.mat')

sample_table = [[] for i in range(25)]

for i in range(0, len(mat['dates'])):
    sample_table[0].append(mat['dates'][i][0][0])

for i in range(0, 1117):
    for j in range(0, 24):
        sample_table[j+1].append(mat['data'][i][j])

filename = 'PV Info\PvData.csv'

if os.path.exists(filename):
    try:
        os.remove(filename)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

with open(filename, 'w', newline='') as csvfile:
    wr = csv.writer(csvfile)
    wr.writerow(['Date', 'Hour', 'PvPower'])
    for j in range(0, len(sample_table[0])):
        for hour in range(1, 25):
            wr.writerow([sample_table[0][j], hour, sample_table[hour][j]])
