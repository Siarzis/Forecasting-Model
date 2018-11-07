import numpy as np
import pandas as pd
import os
import h5py
from numpy.core.multiarray import ndarray
import pvlib
import math


def sol_pos(times_index,latitude,longitude,tz):
    times_index=pd.DatetimeIndex([times_index])
    altitude = 42  # above the sea level in meters

    sand_point = pvlib.location.Location(latitude, longitude, tz=tz, altitude=altitude, name=tz)

    solpos = pvlib.solarposition.get_solarposition(times_index, sand_point.latitude, sand_point.longitude)

    return solpos['apparent_zenith'].values[0]

def read_nwp_solar(pathnwp,date,hor,lat_ind,lon_ind):
    nwp_hour=date.hour
    date_pred=date+pd.DateOffset(hours=int(hor))
    nwps=np.inf
    Flux=np.inf
    if os.path.exists(os.path.join(pathnwp, 'nwp' + date.strftime('%d%m%y') + '.h5')):
        with h5py.File(os.path.join(pathnwp, 'nwp' + date.strftime('%d%m%y') + '.h5'), 'r') as nwpfile:
            try:
                Hflux=np.mean(nwpfile['hor' + str(nwp_hour+hor) + '/Hflux'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()]) / 20  # type: ndarray
                Evap = np.mean(nwpfile['hor' + str(nwp_hour+hor) + '/Evaporation'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()]) * 1e8 / 20
                Flux0 = np.mean(nwpfile['hor' + str(nwp_hour+hor-1) + '/Flux'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()]) / 20
                Flux = nwpfile['hor' + str(nwp_hour+hor) + '/Flux'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()] / 20
                Flux1 = np.mean(nwpfile['hor' + str(nwp_hour+hor + 1) + '/Flux'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()]) / 20
                Cloud = nwpfile['hor' + str(nwp_hour+hor) + '/Cloud'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()] / 20
                Temp = np.mean(nwpfile['hor' + str(nwp_hour+hor) + '/Temperature'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()]) / 300
                Humid = np.mean(nwpfile['hor' + str(nwp_hour+hor) + '/Humidity'].value[lat_ind[0].ravel(),:][:,lon_ind[0].ravel()]) * 1e4 / 20


                solpos1=sol_pos(date_pred,np.mean(lat_ind[0].ravel()),np.mean(lon_ind[0].ravel()),'UTC')

                nwps=np.array([solpos1/180,Hflux,Evap,Flux0,Flux,Flux1,Cloud,Temp,Humid])
                nwpfile.close()
            except:
                pass
    return nwps,Flux

def read_nwp_wind(pathnwp,date,hor,lat_ind,lon_ind):
    nwp_hour=date.hour
    nwps=np.inf
    if os.path.exists(os.path.join(pathnwp, 'nwp' + date.strftime('%d%m%y') + '.h5')):
        with h5py.File(os.path.join(pathnwp, 'nwp' + date.strftime('%d%m%y') + '.h5'), 'r') as nwpfile:
            try:
                Uwind = nwpfile['hor' + str(nwp_hour + hor) + '/U'].value[lat_ind[0].ravel(), :][:,
                        lon_ind[0].ravel()]
                Vwind = nwpfile['hor' + str(nwp_hour + hor) + '/V'].value[lat_ind[0].ravel(), :][:,
                        lon_ind[0].ravel()]
                Temp = np.mean(nwpfile['hor' + str(nwp_hour + hor) + '/Temperature'].value[lat_ind[0].ravel(), :][:,
                               lon_ind[0].ravel()]) / 300
                Pressure = np.mean(
                    nwpfile['hor' + str(nwp_hour + hor) + '/Pressure'].value[lat_ind[0].ravel(), :][:,
                    lon_ind[0].ravel()]) / 1e6

                r2d = 45.0 / math.atan(1.0)
                wspeed = np.asarray(
                    [np.sqrt(np.square(w1) + np.square(w2)) for w1, w2 in zip(Uwind.ravel(), Vwind.ravel())])
                wdir = np.asarray([math.atan2(u, v) * r2d + 180 for u, v in zip(Uwind.ravel(), Vwind.ravel())])
                nwps = np.hstack((wspeed, wdir, Temp, Pressure))

                nwpfile.close()
            except:
                pass
    return nwps

