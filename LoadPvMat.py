import scipy.io
import os
import csv

# mat is a dict data structure
# load .mat file to variable
mat = scipy.io.loadmat('pv_data.mat')

sample_table = [[] for i in range(25)]
print(len(sample_table))

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
    wr.writerow(['Dates', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
                 '17',  '18', '19', '20', '21', '22', '23', '24'])
    for j in range(0, len(sample_table[0])):
        wr.writerow([sample_table[0][j], sample_table[1][j], sample_table[2][j], sample_table[3][j],
                     sample_table[4][j], sample_table[5][j], sample_table[6][j], sample_table[7][j],
                     sample_table[8][j], sample_table[9][j], sample_table[10][j], sample_table[11][j],
                     sample_table[12][j], sample_table[13][j], sample_table[14][j], sample_table[15][j],
                     sample_table[16][j], sample_table[17][j], sample_table[18][j], sample_table[19][j],
                     sample_table[20][j], sample_table[21][j], sample_table[22][j], sample_table[23][j],
                     sample_table[24][j]])
