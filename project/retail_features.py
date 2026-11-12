"""Portable, stateless feature functions required by model.joblib.
Inputs: StockCode, week_start, lag_1 ... lag_13. All lags end before forecast week.
No client data, fitted statistics or future observations are stored here.
"""
import numpy as np
import pandas as pd

LAGS = [f'lag_{i}' for i in range(1, 14)]
NUMERIC = ['lag_1', 'lag_2', 'lag_4', 'lag_13', 'mean_4', 'mean_13', 'std_4', 'zero_share_13', 'week_sin', 'week_cos', 'trend']

def identity(values):
    return values

def nonnegative(values):
    return np.maximum(values, 0)

def make_features(raw, mode='full'):
    data = raw.copy()
    missing = set(['StockCode','week_start']+LAGS) - set(data.columns)
    if missing:
        raise ValueError(f'Missing forecast inputs: {sorted(missing)}')
    dates = pd.to_datetime(data['week_start'], errors='raise')
    if not dates.dt.weekday.eq(0).all():
        raise ValueError('Forecast week_start must be Monday')
    history = data[LAGS].apply(pd.to_numeric, errors='raise')
    if not np.isfinite(history.to_numpy()).all() or (history < 0).any().any():
        raise ValueError('Thirteen complete nonnegative weekly unit lags are required')
    out = pd.DataFrame(index=data.index)
    out['StockCode'] = data.StockCode.astype(str)
    for name in ['lag_1','lag_2','lag_4','lag_13']:
        out[name] = history[name]
    out['mean_4'] = history[LAGS[:4]].mean(axis=1)
    out['mean_13'] = history.mean(axis=1)
    out['std_4'] = history[LAGS[:4]].std(axis=1, ddof=0)
    out['zero_share_13'] = history.eq(0).mean(axis=1)
    week = dates.dt.isocalendar().week.astype(int)
    out['week_sin'] = np.sin(2*np.pi*week/52.1775)
    out['week_cos'] = np.cos(2*np.pi*week/52.1775)
    out['trend'] = (dates-pd.Timestamp('2009-12-07')).dt.days / 7
    if mode == 'no_calendar':
        out[['week_sin','week_cos','trend']] = 0.0
    elif mode == 'no_rolling':
        out[['mean_4','mean_13','std_4','zero_share_13']] = 0.0
    elif mode != 'full':
        raise ValueError(f'Unknown feature mode: {mode}')
    return out
