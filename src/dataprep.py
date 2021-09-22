#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Preparing KNMI data for station:
# STN         LON(east)   LAT(north)  ALT(m)      NAME
# 270         5.752       53.224      1.20        Leeuwarden

import pandas as pd


def get_knmi_data():
    """
    Get and transform the KNMI dataset

    Returns:
        str: File path of the processed CSV data file
    """
    # Import the CSV file and set the column names
    data = pd.read_csv('../input/knmi_raw.csv', skiprows=range(0, 10))
    data.columns = ['station', 'date', 'HH', 'wind', 'temp', 'GHI']

    # Fix datetime index
    data.date = data.date.astype(str)
    data.HH = data.HH.apply(lambda x: str(x).zfill(2))
    data.HH = data.HH.replace('24', '00')
    data['datetime'] = data.date + data.HH + '00'
    data['datetime'] = pd.to_datetime(data.datetime, format='%Y%m%d%H%M')

    # Set the datetime as index and keep only the wind, temperature, and GHI column
    data.index = data.datetime
    data = data[['wind', 'temp', 'GHI']]

    # Fix the units
    data.GHI = data.GHI * 2.77778  # J/cm2 to kW/m2
    data.wind = data.wind / 10  # 0.1m/s to m/s
    data.temp = data.temp / 10  # 0.1m/s to m/s

    # Fix timezone UTC
    data.index = data.index.tz_localize('UTC')

    # Export to new csv
    file_path = '../input/knmi_processed.csv'
    data.to_csv(file_path, sep=";")
    return file_path
