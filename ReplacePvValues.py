import pandas as pd
import numpy as np

pv_data = pd.read_csv('PV Info\PvData.csv')

nan_indexes = pd.isnull(pv_data).any(1).nonzero()[0]

print(nan_indexes)
