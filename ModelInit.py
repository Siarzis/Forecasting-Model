from distutils.dir_util import copy_tree

import numpy as np
import pandas as pd

import pickle
import os
import shutil
import logging
import h5py


def column_names(data_type, size):

    columns = []

    if data_type == 'pv':
        columns.append('power')
        columns.append('power.0')
        columns.append('hflux')
        columns.append('evap')
        columns.append('other')
        for s in range(size):
            columns.append('flux.' + str(s))
        columns.append('other')
        for s in range(size):
            columns.append('cloud.' + str(s))
        columns.append('temp')
        columns.append('humid')
        columns.append('hour')
        columns.append('month')
        columns.append('horizon')
    elif data_type == 'wind':
        columns.append('power')
        for s in range(size):
            columns.append('wind.' + str(s))
        for s in range(size):
            columns.append('direction.' + str(s))
        columns.append('temp')
        columns.append('pressure')
        columns.append('hour')
        columns.append('month')
        columns.append('horizon')
    elif data_type == 'load':
        columns = ['sp_day', 'hour', 'month'] + ['other.' + str(n) for n in range(75)]
    else:
        columns = np.inf
    # future warning is here
    if np.isreal(columns):
        raise ValueError('Wrong application type. Cannot shape input columns')
    return columns


def coordinates(pathnwp, lats, lons):
    try:
        latlonfile = h5py.File(os.path.join(pathnwp, 'latslons.h5'), 'r')
        latnwp = latlonfile['lats']
        lonnwp = latlonfile['lons']
        lat_ind = np.where((latnwp.value[:, 0] >= lats[0] - 0.05) & (latnwp.value[:, 0] <= lats[-1] + 0.05))
        lon_ind = np.where((lonnwp.value[0, :] >= lons[0] - 0.05) & (lonnwp.value[0, :] <= lons[-1] + 0.05))
    except:
        raise IOError('Cannot find latslons.h5')

    return lat_ind, lon_ind


class ForecastModel(object):

    def __init__(self, model_path, path_nwp='/media/sf_F_DRIVE/NWP_h5', rated=pd.DataFrame([100], columns=['rated']),
                 coord=pd.DataFrame(np.array([38, 28])[np.newaxis, :], columns=['latitude', 'longitude']),
                 problem_type='pv', threshold_split=0.5, threshold_act=0.005, n_clusters=200):
        if not isinstance(rated, pd.DataFrame) or not isinstance(coord, pd.DataFrame):
            raise ValueError('Coordinates and Rated should be pandas dataframe')
        self.rated = rated.rated.values[0]
        self.model_path = model_path
        self.path_nwp = path_nwp
        self.type = problem_type
        if coord.shape[1] > 2:
            raise IOError('Wrong format on coordinates array')
        self.columns = column_names(problem_type, coord.shape[0])
        self.lats = [coord.latitude.min(), coord.latitude.max()]
        self.lons = [coord.longitude.min(), coord.longitude.max()]
        self.threshold_split = threshold_split
        self.threshold_act = threshold_act
        self.n_clusters = n_clusters

    def init_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(os.path.join(self.model_path, 'log_run.log'), mode='w+')
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(handler)
        self.logger = logger

    def init_files(self):
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
        for the_file in os.listdir(self.model_path):
            file_path = os.path.join(self.model_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
        copy_tree('./fuzzy_models', os.path.join(self.model_path, 'fuzzy_models'))

    def load(self):
        if os.path.exists(os.path.join(self.model_path, 'model' + '.pickle')):
            try:
                f = open(os.path.join(self.model_path, 'model' + '.pickle'), 'rb')
                tmp_dict = pickle.load(f)
                f.close()
                self.__dict__.update(tmp_dict)
            except:
                self.save()
        else:
            self.save()

    def save(self):
        f = open(os.path.join(self.model_path, 'model' + '.pickle'), 'wb')
        dict = {}
        for k in self.__dict__.keys():
            if k not in ['logger']:
                dict[k] = self.__dict__[k]
        pickle.dump(dict, f)
        f.close()


data_type = 'pv'
pathnwp = 'C:/Users/User/WorkSpace/Docker-Network/h5_files'
model_path = 'C:/Users/User/WorkSpace/Docker-Network/ModelPath'
rated = pd.read_csv('rated.csv')
coord = pd.read_csv('coordinates.csv')

model = ForecastModel(model_path, path_nwp=pathnwp, problem_type=data_type, rated=rated, coord=coord)
model.init_logger()
model.init_files()
model.save()
