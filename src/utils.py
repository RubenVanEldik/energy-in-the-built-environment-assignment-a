# -*- coding: utf-8 -*-

import pandas as pd
from scipy import stats
import pvlib


def compare_series(series_a, series_b):
    """
    Calculate the RMSE, MBE, and MAE for two data series

    Parameters:
        series_a (Series): First pandas series
        series_b (Series): Second pandas series

    Returns:
        obj: Object with the 'rmse', 'mbe', 'mae', 'rsqr' values
    """
    return {
        'rmse': ((series_a - series_b) ** 2).mean() ** 0.5,
        'mbe': (series_a - series_b).mean(),
        'mae': abs(series_a - series_b).mean(),
        'rsqr': stats.linregress(series_a, series_b).rvalue ** 2
    }


def print_object(dict, *, name='', uppercase=False):
    """
    Print the values of an object nicely on a single line

    Parameters:
        dict (dict): Dictionary that should be printed
        name (string): Name that should appear before the first key/value of the dictionary
        uppercase (bool): Whether or not the keys should be printed in capital letters

    Returns:
        null
    """
    string = name.ljust(10) if name != '' else ''
    for key in dict:
        string += f'{key.upper() if uppercase else key}: {"" if dict[key] < 0 else " "}{float(dict[key]):.4}'.ljust(
            len(key) + 10)

    print(string)


def get_irradiance(filename, *, latitude, longitude, index_col='timestamp', temp_col):
    """
    Get the irradiance and position of the sun and merge this with the original DataFrame

    Parameters:
        filename (string): Name of the CSV file with the irradiance data
        latitude (float): Latitude
        longitude (float): Longitude
        index_col (string): Name of the column that should be used as index (default is timestamp)
        temp_col (string): Name of the column with the temperature 

    Returns:
        DataFrame: A concatenated DataFrame of the input file with the solar info, the solar info columns start with 'solar_'
    """
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
