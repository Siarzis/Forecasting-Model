from pymongo import MongoClient

import time
import pygrib
import pandas as pd
import os

start_time = time.time()

client = MongoClient('localhost', 27017)  # establish database connection
client.drop_database('nwp')
db = client.nwp  # access database


def grib2dict(t):

    mapbased = db['mapbased'+t.strftime('%d%m%y')]  # specify which collection we’ll be using

    documents = []

    for i in range(120):
        for j in range(189):
            documents.append({'coordinates': j+189*i,
                              'elements': {'U': [], 'V': [], 'Humidity': [], 'Cloud': [], 'Flux': [],
                                           'Evaporation': [], 'Hflux': []}
                              })

    for hor in range(0, 120):
        print('/mnt/hgfs/NWP/2016_' + t.strftime('%m') + '/MFSTEP_IASA_00' + t.strftime('%d%m%y')
         + '_' + str(hor).zfill(3) + '.grb')
        filename = os.path.join('/mnt/hgfs/NWP/2016_' + t.strftime('%m') + '/MFSTEP_IASA_00' + t.strftime('%d%m%y')
                                + '_' + str(hor).zfill(3) + '.grb')

        if os.path.exists(filename):
            try:
                grb = pygrib.open(filename)
                g = grb.message(1)
                x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)
                u_map = x[0].tolist()
                g = grb.message(2)
                x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)
                v_map = x[0].tolist()
                g = grb.message(4)
                x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)
                humidity_map = x[0].tolist()
                g = grb.message(5)
                x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)
                cloud_map = x[0].tolist()
                g = grb.message(8)
                x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)
                flux_map = x[0].tolist()
                g = grb.message(12)
                x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)
                evaporation_map = x[0].tolist()
                g = grb.message(4)
                x = g.data(lat1=33, lat2=45, lon1=12, lon2=31)
                hflux_map = x[0].tolist()

                for i in range(len(u_map)):
                    for j in range(len(u_map[0])):
                        documents[j+189*i]['elements']['U'].append(u_map[i][j])
                        documents[j+189*i]['elements']['V'].append(v_map[i][j])
                        documents[j+189*i]['elements']['Humidity'].append(humidity_map[i][j])
                        documents[j+189*i]['elements']['Cloud'].append(cloud_map[i][j])
                        documents[j+189*i]['elements']['Flux'].append(flux_map[i][j])
                        documents[j+189*i]['elements']['Evaporation'].append(evaporation_map[i][j])
                        documents[j+189*i]['elements']['Hflux'].append(hflux_map[i][j])
                grb.close()

            except:
                continue
                # raise Exception('Could not open grib file.')
        else:
            print('File does not exist')
    for i in range(len(documents)):
        mapbased.insert_one(documents[i])


times_index = pd.date_range(start='01/01/2016', end='09/30/2016')

count = 1
for t in times_index:
    grib2dict(t)
    print(count)
    count += 1
    elapsed_time = time.time() - start_time
    print(elapsed_time)
