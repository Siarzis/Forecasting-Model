from distutils.dir_util import copy_tree
from pymongo import MongoClient

import numpy as np
import pandas as pd

import os
import shutil
import logging
import h5py


class ForecastModel(object):

    def __init__(self, model_path, path_nwp, rated, coord, problem_type, threshold_split, threshold_act, n_clusters):

        if not isinstance(rated, pd.DataFrame) or not isinstance(coord, pd.DataFrame):
            raise ValueError('Coordinates and Rated should be pandas dataframe')
        self.rated = rated.rated.values[0]
        self.model_path = model_path
        self.path_nwp = path_nwp
        self.type = problem_type
        if coord.shape[1] > 2:
            raise IOError('Wrong format on coordinates array')
        self.columns = []
        self.lats = [coord.latitude.min(), coord.latitude.max()]
        self.lons = [coord.longitude.min(), coord.longitude.max()]
        self.coord = coord
        self.threshold_split = threshold_split
        self.threshold_act = threshold_act
        self.n_clusters = n_clusters
        self.lat_ind = []
        self.long_ind = []

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

    def column_names(self):
        if self.type == 'pv':
            self.columns = ['power', 'power.0', 'hflux', 'evap', 'other']
            for s in range(self.coord.shape[0]):
                self.columns.append('flux.' + str(s))
            self.columns.append('other')
            for s in range(self.coord.shape[0]):
                self.columns.append('cloud.' + str(s))
            self.columns = ['temp', 'humid', 'hour', 'month', 'horizon']
        elif self.type == 'wind':
            self.columns = ['power']
            for s in range(self.coord.shape[0]):
                self.columns.append('wind.' + str(s))
            for s in range(self.coord.shape[0]):
                self.columns.append('direction.' + str(s))
            self.columns = ['temp', 'pressure', 'hour', 'month', 'horizon']
        elif self.type == 'load':
            self.columns = ['sp_day', 'hour', 'month'] + ['other.' + str(n) for n in range(75)]
        else:
            self.columns = np.inf
        # future warning is here
        if np.isreal(self.columns):
            raise ValueError('Wrong application type. Cannot shape input columns')

    def coordinates(self, pathnwp):
        try:
            latlonfile = h5py.File(os.path.join(pathnwp, 'latslons.h5'), 'r')
            latnwp = latlonfile['lats']
            lonnwp = latlonfile['lons']
            self.lat_ind = np.where((latnwp.value[:, 0] >= self.lats[0] - 0.05) & (latnwp.value[:, 0] <= self.lats[-1] + 0.05))
            self.long_ind = np.where((lonnwp.value[0, :] >= self.lons[0] - 0.05) & (lonnwp.value[0, :] <= self.lons[-1] + 0.05))
        except:
            raise IOError('Cannot find latslons.h5')

    def store_model(self):
        client = MongoClient('localhost', 27017)  # establish database connection

        client.drop_database('nwp')
        db = client.nwp  # access database

        # TODO maybe 'coordinates' & 'column_names' functions will be used here
        models = db.models
        doc = {'latitude': self.lat_ind, 'longitude': self.long_ind, 'columns': self.columns}

        models.insert_one(doc)


p_nwp = 'C:/Users/User/WorkSpace/Docker-Network/h5_files'
m_p = 'C:/Users/User/WorkSpace/Docker-Network/ModelPath'
p_t = 'pv'
c = pd.DataFrame(np.array([38, 28])[np.newaxis, :], columns=['latitude', 'longitude'])
r = pd.DataFrame([100], columns=['rated'])
t_s = 0.5
t_a = 0.005
n_c = 200

model = ForecastModel(model_path=m_p, path_nwp=p_nwp, problem_type=p_t, rated=r, coord=c, threshold_split=t_s,
                      threshold_act=t_a, n_clusters=n_c)
model.init_logger()
model.init_files()
