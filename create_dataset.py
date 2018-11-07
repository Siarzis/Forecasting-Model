import numpy as np
import pandas as pd
from pytz import timezone
from distutils.dir_util import copy_tree
import os, shutil
from Training_set.read_nwp_funcs import read_nwp_solar, read_nwp_wind
from Initialize_model.Model_init import Forecast_model,coordinates

def sp_index(r, holidays):
    if r.date() in [h.date() for h in pd.to_datetime(holidays.date).tolist()]:
        return 20
    elif r.dayofweek == 6:
        return 10
    else:
        return 0


def datetime_exists_in_tz(dt, tz):
    try:
        dt.tz_localize(tz)
        return True
    except:
        return False


def read_load(ld_ts, tp_ts, holidays, columns, hor):
    if hor==24:
        lags2 = np.hstack([np.arange(24, 37), np.arange(48, 51), np.arange(72, 75), np.arange(96, 99), 120, 144, np.arange(168, 177), 192,
                                    np.arange(8736, 8742), 8760, 8736 + 168])
    elif hor==1:
        lags2 = np.hstack(
            [np.arange(1, 37), np.arange(48, 51), np.arange(72, 75), np.arange(96, 99), 120, 144, np.arange(168, 177),
             192,
             np.arange(8736, 8742), 8760, 8736 + 168])

    rated = ld_ts.max()
    
    data_upd = pd.DataFrame(columns=columns)
    target_upd = pd.Series(name='target')
    for r in ld_ts.index[9000:]:
        min_temp = []
        max_temp = []
        energy = []
        sp = []
        for l in [0, 1, 2, 3, 4, 5, 6, 7]:
            daily = pd.date_range(r.date() - pd.DateOffset(days=int(l)), periods=24, freq='H')
            energy.append(ld_ts.loc[daily].apply(lambda x: x / rated).sum())
            max_temp.append(tp_ts.loc[daily].max())
            min_temp.append(tp_ts.loc[daily].min())
            sp.append(sp_index(r - pd.DateOffset(days=int(l)), holidays))
        energy = np.array(energy[1:]) / 24
        max_temp = np.asarray(max_temp)
        min_temp = np.asarray(min_temp)
        sp = np.asarray(sp)
        date_inp2 = [r - pd.DateOffset(hours=int(l)) for l in lags2]
        hr = r.hour
        mnth = r.month
        dayweek = r.dayofweek + 1
        yr = r.year / 2008
        try:
            inp = pd.Series(np.hstack(
                [sp[0], hr, mnth, dayweek, yr, ld_ts.loc[date_inp2] / rated, tp_ts.loc[r] / 110,
                 max_temp / 110, min_temp / 110, sp[1:] / 20, energy]), index=columns, name=r)
            targ = pd.Series(ld_ts.loc[r], index=[r], name='target')
            if not inp.isnull().any() and not targ.isnull().any():
                data_upd = data_upd.append(inp)
                target_upd = target_upd.append(targ)
        except:
            continue
    return data_upd, target_upd


def read_solar(ts_data,rated, lat_ind, lon_ind,  pathnwp, columns,hor):
    data_upd = pd.DataFrame(columns=columns)
    target_upd = pd.Series(name='target')
    for r in ts_data.index:
        date = r
        date_pred = date + pd.DateOffset(hours=int(hor))
        hr = date_pred.hour
        mnth = date_pred.month
        nwps, Flux=read_nwp_solar(pathnwp, date, hor, lat_ind, lon_ind)

        if isinstance(nwps,np.ndarray):
            if Flux > 1e-7:
                power = ts_data.data.loc[date_pred - pd.DateOffset(hours=int(1))] / rated
                inp = pd.Series(np.hstack([power, nwps, hr, mnth, hor]), index=columns, name=date_pred)
                targ = pd.Series(ts_data.data.loc[date_pred], index=[date_pred], name='target')
                if not inp.isnull().any() and not targ.isnull().any():
                    data_upd = data_upd.append(inp)
                    target_upd = target_upd.append(targ)
    return data_upd, target_upd


def read_wind(ts_data,rated, lat_ind, lon_ind,  pathnwp, columns,hor):
    data_upd = pd.DataFrame(columns=columns)
    target_upd = pd.Series(name='target')
    for r in ts_data.index:
        date = r
        date_pred = date + pd.DateOffset(hours=int(hor))
        hr = date_pred.hour
        mnth = date_pred.month
        nwps, Flux=read_nwp_wind(pathnwp, date, hor, lat_ind, lon_ind)
        if isinstance(nwps,np.ndarray):
            power = ts_data.data.loc[date_pred - pd.DateOffset(hours=int(1))] / rated
            inp = pd.Series(np.hstack([power, nwps, hr, mnth, hor]), index=columns, name=date_pred)
            targ = pd.Series(ts_data.data.loc[date_pred], index=[date_pred], name='target')
            if not inp.isnull().any() and not targ.isnull().any():
                data_upd = data_upd.append(inp)
                target_upd = target_upd.append(targ)
    return data_upd, target_upd


def create_dataset(model, hor):
    
    ts_data=pd.read_csv('data.csv',index_col=0,parse_dates=True)
    if model.type in {'pv', 'wind'}:
        # ts_data = ts_data.loc[ts_data["dates"].apply(datetime_exists_in_tz, tz=timezone('Europe/Athens'))]
        # ts_data.set_index("dates", inplace=True)
        # ts_data.index = ts_data.index.tz_localize(timezone('Europe/Athens'))
        # ts_data.index = ts_data.index.tz_convert(timezone('UTC'))
        #
        # ts_data.dates=pd.to_datetime(ts_data.dates)
        # ts_data = ts_data.sort_values('dates')
        # ts_data.set_index("dates", inplace=True)

        if model.type=='pv':
            X, y = read_solar(ts_data, model.rated, model.lat_ind, model.lon_ind, model.path_nwp, model.columns, hor)
        else:
            X, y = read_wind(ts_data, model.rated, model.lat_ind, model.lon_ind, model.path_nwp, model.columns, hor)
    elif model.type=='load':
        temp_ts = pd.read_csv(os.path.join(model.path_data,'temperature.csv'))
        holidays = pd.read_csv(os.path.join(model.path_data, 'holidays.csv'))
        columns = ['sp_day', 'hour', 'month'] + ['other.' + str(n) for n in range(75)]
        X, y = read_load(ts_data, temp_ts, holidays, columns, hor)
    else:
        raise NotImplemented('Wrong application type')
    return X, y

if __name__=='__main__':
    model_path = 'C:/Users/joe/PycharmProjects/RUN_MODELS/ModelPath'
    model=Forecast_model(model_path)
    model.load()
    model.lat_ind, model.lon_ind = coordinates(model.path_nwp, model.lats, model.lons)
    model.save()
    hor=1
    X, y = create_dataset(model, hor)
    X.to_csv(os.path.join(model.model_path,'training_inputs.csv'))
    y.to_csv(os.path.join(model.model_path,'training_targets.csv'))