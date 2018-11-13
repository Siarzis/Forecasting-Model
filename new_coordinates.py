import pygrib
import pandas as pd
import numpy as np

file = '/mnt/hgfs/NWP/2016_01/MFSTEP_IASA_00010116_000.grb'

grb = pygrib.open(file)
g = grb.message(1)
x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)

latitudes = x[1]
longitudes = x[2]

index = []

for i in latitudes:
    index.append(i[0])

print(len(latitudes))
print(len(longitudes))

A = np.arange(len(index)*len(longitudes[0]), dtype=int)

rated = pd.DataFrame(np.reshape(A, (-1, len(longitudes[0]))), index=index, columns=longitudes[0])
print(rated)
