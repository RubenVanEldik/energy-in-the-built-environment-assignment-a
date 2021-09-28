import math

import pandas as pd

from utils import pv


def prepare_data():
    """
    Get and transform the KNMI dataset.

    Returns:
        str: File path of the processed CSV data file
    """
    # Import the CSV file and set the column names
    knmi = pd.read_csv('../input/knmi_raw.csv', skiprows=range(0, 10))
    knmi.columns = ['station', 'date', 'HH', 'wind', 'temp', 'GHI']

    # Fix datetime index
    knmi.date = knmi.date.astype(str)
    knmi.HH = knmi.HH.apply(lambda hour: str(hour).zfill(2))
    knmi.HH = knmi.HH.replace('24', '00')
    knmi['HH'] = ((knmi.HH.apply(int) - 1) % 24).apply(str)
    knmi['datetime'] = knmi.date + knmi.HH + '00'
    knmi['datetime'] = pd.to_datetime(knmi.datetime, format='%Y%m%d%H%M')

    # Set the datetime as index and keep only the wind, temperature, and GHI column
    knmi.index = knmi.datetime
    knmi = knmi[['wind', 'temp', 'GHI']]

    # Fix the units
    knmi.GHI = knmi.GHI * 100 ** 2 / 60 / 60  # J/cm2 to kW/m2
    knmi.wind = knmi.wind / 10  # 0.1m/s to m/s
    knmi.temp = knmi.temp / 10  # 0.1m/s to m/s

    # Fix timezone UTC
    knmi.index = knmi.index.tz_localize('UTC')

    # Export to new csv
    file_path = '../output/question2/knmi.csv'
    knmi.to_csv(file_path, sep=';')
    return file_path


def get_irradiance():
    """
    Get the KNMI data and calculate the irradiance for each timestep.

    Returns:
        DataFrame: Single DataFrame with all weather and irradiance data
    """
    latitude = 53.224
    longitude = 5.752

    # Get the irradiance data from the KNMI data
    filename = prepare_data()
    irradiance = pv.get_irradiance(filename, latitude=latitude, longitude=longitude, index_col='datetime', temp_col='temp')

    # Get the DNI and DHI
    irradiance['DNI'] = pv.calculate_dni('dirindex', irradiance, latitude=latitude, longitude=longitude)
    irradiance['DHI'] = irradiance.GHI - irradiance.DNI * irradiance.solar_zenith.apply(math.cos)
    return irradiance
