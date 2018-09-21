import numpy as np
import pandas as pd
import os
from sklearn.externals import joblib
import skfuzzy as fuzz
import difflib
import re

# Cluster layer class read the pre-trained rules from csv (obtained by Cluster_layer_test.py),
# compute the rules activations in a DataSet and create the data for each cluster for the RBF layer.
# Also check the input format and the variables range


class Clustering(object):

    # init defines input variables needed to call Clustering class
    def __init__(self, rule_filename, fuzzy_models_path, variables_names, output_path, is_trained=False,
                 problem_type='pv', thres_split=0.5, thres_act=0.005, n_clusters=100):

        self.is_trained = is_trained
        self.rule_filename = rule_filename
        self.variables = variables_names
        self.columns = set([re.sub(r'\W\d*', '', var) for var in variables_names])
        self.type = problem_type
        self.thres_split = thres_split
        self.thres_act = thres_act
        self.output_path = output_path
        self.n_clusters = n_clusters

        if self.type == 'pv':
            self.fnames = ['cloud', 'flux', 'horizon', 'hour_pv', 'month', 'temp', 'humid', 'hflux', 'evap', 'power']
            self.p = 4
        elif self.type == 'wind':
            self.fnames = ['wind', 'direction', 'horizon', 'hour_wind', 'month', 'temp', 'power', 'pressure']
            self.p = 3

        fmodel = {}
        for name in self.fnames:
            fmodel[name] = joblib.load(os.path.join(fuzzy_models_path, name + '.pkl'))
        self.fmodel = fmodel

    def add_rule(self, x):
        self.rules = self.rules.append(pd.Series(np.ones([1, len(self.columns)])[0].tolist(),
                                                 index=self.columns), ignore_index=True)

        vars_names = set([re.sub(r'\W\d*', '', var) for var in x.index])
        for var in vars_names:
            cols = [c for c in x.index if re.sub(r'\W\d*', '', c) == var]

            name = difflib.get_close_matches(var, self.fnames)
            fm = self.fmodel[name[0]]
            data = x[cols]

            if isinstance(data, pd.DataFrame):
                data = data.mean(axis=1).tolist()
            else:
                data = np.mean(data.tolist())
            act = []
            mfs = []
            for mf_name, mf in fm.items():
                if mf_name not in 'universe':
                    act.append(fuzz.interp_membership(fm['universe'], mf, data))
                    mfs.append(mf_name)
            act = np.array(act)
            mfs = np.array(mfs)
            mf_ind = np.argmax(act, axis=0)
            mfs = mfs[mf_ind]

            if np.isscalar(mfs):
                self.rules[var].iloc[-1] = mfs
            else:
                self.rules[var].iloc[-1] = mfs[0]

    def compute_activations(self, df):

        activations = []
        rule_name = []

        for i, r in self.rules.iterrows():
            act = []
            if isinstance(df, pd.DataFrame):
                df_vars=df.columns
            elif isinstance(df, pd.Series):
                df_vars=df.index
            vars_names = set([re.sub(r'\W\d*', '', var) for var in df_vars])
            for var in vars_names:
                cols = [c for c in df_vars if re.sub(r'\W\d*', '', c) == var]
                name = difflib.get_close_matches(var, self.fnames)
                fm = self.fmodel[name[0]]
                data = df[cols]
                if isinstance(data, pd.DataFrame):
                    data = data.mean(axis=1).tolist()
                elif isinstance(data, pd.Series):
                    data = data.mean().tolist()
                else:
                    data = data.tolist()
                act.append(fuzz.interp_membership(fm['universe'], fm[r[var]], data))
                # act1 = fuzz.interp_membership(fm['universe'], fm[r[col]], data)

            activations.append(np.power(np.prod(np.array(act), axis=0), 1 / self.p))
            rule_name.append('rule_' + str(i))

        if isinstance(df, pd.DataFrame):
            Activations = pd.DataFrame(np.array(activations).T, columns=rule_name)
        elif isinstance(df, pd.Series):
            Activations = pd.Series(np.array(activations).T, index=rule_name)

        return Activations

    def init_rules(self):
        return pd.DataFrame(columns=self.columns)

    def train(self, X):
        if self.rules.empty:
            ind = np.random.randint(0, len(X)-1)
            self.add_rule(X.iloc[ind])
        df_act = self.compute_activations(X)
        min_old = df_act.max(axis=1).min()

        while df_act.max(axis=1).min() <= self.thres_split and len(self.rules)<=self.n_clusters:
            ind = df_act.max(axis=1).idxmin()
            self.add_rule(X.iloc[ind])
            df_act = self.compute_activations(X)
            print(len(self.rules), df_act.max(axis=1).min())
            print([df_act['rule_' + str(i)].where(df_act['rule_' + str(i)] >= self.thres_act).count() for i in self.rules.index])
            if df_act.max(axis=1).min() + np.finfo('float32').eps <= min_old and min_old >= 0.01:
                break
            min_old = df_act.max(axis=1).min()

        self.rules = self.rules.drop_duplicates()
        self.rules.to_csv(self.rule_filename, index=False)

    def check_data(self, X):
        if not isinstance(X, pd.DataFrame):
            try:
                X = pd.DataFrame(X, columns=self.columns)
            except ValueError:
                print('Ooops cannot convert dataset to a pandas Dataframe')
        vars_names = set([re.sub(r'\W\d*','',var) for var in X.columns])
        if len(vars_names) != len(self.columns) or not all(n in self.columns for n in vars_names) or \
                not all(n in vars_names for n in self.columns):
            raise ValueError('The variables in dataset have different names from these are set in initialization')
        for var in vars_names:
            cols = [col for col in X.columns if var in col]
            for c in cols:
                name = difflib.get_close_matches(c, self.fnames)[0]
                check_range = X[c].between(self.fmodel[name]['universe'][0],self.fmodel[name]['universe'][-1]).all()
                if not check_range:
                    raise ImportError('variable ' + c + ' is not in right range')
        return X

    def update(self, X):

        X = self.check_data(X)

        if os.path.exists(self.rule_filename):
            try:
                self.rules = pd.read_csv(self.rule_filename)
            except IOError as err:
                print("Cannot open the file with rules: {0}".format(err))
        else:
            # TODO define rules inside __init__
            self.rules = self.init_rules()

        if not self.is_trained:
            self.train(X)

        if os.path.exists(os.path.join(self.output_path, 'dataset.csv')):
            data = pd.read_csv(os.path.join(self.output_path, 'dataset.csv'))
            data = data.append(X)
        else:
            data = X.copy(deep=True)

        data = data.round(8)
        data = data.drop_duplicates()
        data.to_csv(os.path.join(self.output_path, 'dataset.csv'),index=False)
        # TODO define activations inside __init__
        self.activations = self.compute_activations(data)
