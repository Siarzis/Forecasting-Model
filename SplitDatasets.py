import pandas as pd
import time

start_time = time.time()

k = 1

farm_data = pd.read_csv('Wind Info\WindFarm' + str(k+1) + '.csv')

columns = ['Dates', 'SetPoints', 'WindSpeed', 'WindDirection']
training_dataset = pd.DataFrame(columns=columns)
testing_dataset = pd.DataFrame(columns=columns)

for i, row in farm_data.iterrows():
    # (farm_data['SetPoints'].loc[i])
    if farm_data['SetPoints'].loc[i] == 1.0:
        sample_df = pd.DataFrame([row.tolist()], columns=columns)
        training_dataset = training_dataset.append(sample_df, ignore_index=True)
    else:
        sample_df = pd.DataFrame([row.tolist()], columns=columns)
        testing_dataset = testing_dataset.append(sample_df, ignore_index=True)

print(training_dataset)
print(testing_dataset)

elapsed_time = time.time() - start_time
print(elapsed_time)
