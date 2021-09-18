# -*- coding: utf-8 -*-

from scipy import stats

def compare_series(series_a, series_b):
    """Return the RMSE, MBE, and MAE for two data series"""
    return {
        'rmse': ((series_a - series_b) ** 2).mean() ** 0.5,
        'mbe': (series_a - series_b).mean(),
        'mae': abs(series_a - series_b).mean(),
        'rsqr': stats.linregress(series_a, series_b).rvalue ** 2
    }
