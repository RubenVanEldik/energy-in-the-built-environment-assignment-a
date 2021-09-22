# -*- coding: utf-8 -*-

import pandas as pd
from scipy import stats
import pvlib


def compare_series(series_a, series_b):
    """Return the RMSE, MBE, and MAE for two data series"""
    return {
        'rmse': ((series_a - series_b) ** 2).mean() ** 0.5,
        'mbe': (series_a - series_b).mean(),
        'mae': abs(series_a - series_b).mean(),
        'rsqr': stats.linregress(series_a, series_b).rvalue ** 2
    }


def print_object(dict, *, name='', uppercase=False):
    string = name.ljust(10) if name != '' else ''
    for key in dict:
        string += f'{key.upper() if uppercase else key}: {"" if dict[key] < 0 else " "}{float(dict[key]):.4}'.ljust(
            len(key) + 10)

    print(string)


def get_irradiance(filename, *, latitude, longitude, index_col='timestamp', temp_col):
    # Return the irradiance and position of the sun
    # TODO: check if dataset exists in UTC timezone.
    irradiance = pd.read_csv(filename,
                             sep=";", index_col=index_col, parse_dates=True)
    solar_position = pvlib.solarposition.ephemeris(
        irradiance.index, latitude, longitude, temperature=irradiance[temp_col])

    for column in solar_position:
        new_column_name = column if column.startswith(
            'solar') else f'solar_{column}'
        irradiance[new_column_name] = solar_position[column]

    # Remove all timestamps where the solar elevation is less than 4
    return irradiance[irradiance.solar_elevation > 4]
