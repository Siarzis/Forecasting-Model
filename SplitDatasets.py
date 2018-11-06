import pandas as pd
import os
import time

start_time = time.time()

k = 0

farm_data = pd.read_csv('Wind Info\WindFarm' + str(k+1) + '.csv')

columns = ['Dates', 'SetPoints', 'WindSpeed', 'WindDirection']
training_dataSet = pd.DataFrame(columns=columns)
testing_dataSet = pd.DataFrame(columns=columns)

for i, row in farm_data.iterrows():
    if farm_data['SetPoints'].loc[i] == 1.0:
        virtual_df = pd.DataFrame([row.tolist()], columns=columns)
        training_dataSet = training_dataSet.append(virtual_df, ignore_index=True)
    else:
        virtual_df = pd.DataFrame([row.tolist()], columns=columns)
        testing_dataSet = testing_dataSet.append(virtual_df, ignore_index=True)

print(training_dataSet)
print(testing_dataSet)

filename = 'DataSets\Training DataSet.csv'
if os.path.exists(filename):
    try:
        os.remove(filename)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
training_dataSet.to_csv(filename, index=False)

filename = 'DataSets\Testing DataSet.csv'
if os.path.exists(filename):
    try:
        os.remove(filename)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
testing_dataSet.to_csv(filename, index=False)

elapsed_time = time.time() - start_time
print(elapsed_time)
