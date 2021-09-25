# -*- coding: utf-8 -*-

import json
import math
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
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


def save_json_file(obj, *, filepath):
    """
    Save a object or list as a JSON file

    Parameters:
        obj (dict or list): Dictionary or list that should be stored
        filepath (string): Path of where the JSON file should be stored
    """
    with open(filepath, 'w') as fp:
        json.dump(obj, fp, indent=2, ensure_ascii=False)

def save_text_file(text, *, filepath):
    """
    Save a string as a text file

    Parameters:
        text (str): String that should be stored
        filepath (string): Path of where the JSON file should be stored
    """
    with open(filepath, 'w') as output:
        output.write(text)


def savefig(filepath):
    """
    Print the values of an object nicely on a single line

    Parameters:
        filepath (str): Path where the figure should be saved
    """
    plt.savefig(filepath, dpi=250, bbox_inches='tight', pad_inches=0.2)


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
    file_path = '../output/question2/knmi.csv'
    data.to_csv(file_path, sep=";")
    return file_path


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


def calculate_dni(model, irradiance, *, latitude, longitude):
    """
    Calculate the DNI based on the model, irradiance, and solar position

    Parameters:
        model (string): The name of the model, has to be either 'disc', 'dirint', 'dirindex', or 'erbs'
        irradiance (DataFrame): The latitude

    Returns:
        Series: The DNI series
    """
    # Define important variables
    time = irradiance.index
    ghi = irradiance.GHI
    zenith = irradiance['solar_zenith']
    apparent_zenith = irradiance['solar_apparent_zenith']

    # Calculate and return the DNI for a specific type
    if model == 'disc':
        return pvlib.irradiance.disc(ghi, zenith, time).dni
    if model == 'dirint':
        return pvlib.irradiance.dirint(ghi, zenith, time)
    if model == 'dirindex':
        relative_airmass = pvlib.atmosphere.get_relative_airmass(
            apparent_zenith)
        absolute_airmass = pvlib.atmosphere.get_absolute_airmass(
            relative_airmass)
        linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(
            time, latitude, longitude)
        clearsky = pvlib.clearsky.ineichen(
            apparent_zenith, absolute_airmass, linke_turbidity, perez_enhancement=True)
        return pvlib.irradiance.dirindex(ghi, clearsky['ghi'], clearsky['dni'], zenith=zenith, times=time)
    if model == 'erbs':
        return pvlib.irradiance.erbs(ghi, zenith, time).dni
    raise Exception('Invalid GHI-DNI model type')


def get_ac_from_dc(p_dc, p_ac0, *, efficiency_nom=0.96):
    """
    Calculate AC power output of the inverter for a specific DC power

    Parameters:
        p_dc (float or int): The DC power of the solar panels
        p_ac0 (float or int): Rated power of the inverter, equal to the rated DC power of the PV system

    Returns:
        float: The efficiency of the inverter
    """
    # Return 0 if the DC power is 0
    if p_dc == 0:
        return 0

    # Calculate the rated DC power and zeta
    p_dc0 = p_ac0 / efficiency_nom
    zeta = p_dc / p_dc0
    
    # Return the rated power of the inverter if the DC power is larger or equal to the rated DC power
    if p_dc >= p_dc0:
        return p_ac0

    # Calculate the efficiency
    efficiency = -0.0162 * zeta - (0.0059 / zeta) + 0.9858

    # Return the efficiency of the inverter times the DC power
    return efficiency * p_dc


def get_knmi_irradiance():
    """
    Get the KNMI data and calculate the irradiance for each timestep

    Returns:
        DataFrame: Single DataFrame with all weather and irradiance data
    """
    latitude = 53.224
    longitude = 5.752

    # Get the irradiance data from the KNMI data
    filename = get_knmi_data()
    irradiance = get_irradiance(filename, latitude=latitude, longitude=longitude, index_col='datetime', temp_col='temp')
    
    # Get the DNI and DHI
    irradiance['DNI'] = calculate_dni('dirindex', irradiance, latitude=latitude, longitude=longitude)
    irradiance['DHI'] = irradiance.GHI - irradiance.DNI * irradiance.solar_zenith.apply(math.cos)
    return irradiance


def calculate_power_output(irradiance, module, *, tilt, azimuth):
    # Define some variables
    wind = irradiance.wind
    temp_air = irradiance.temp
    solar_zenith = irradiance.solar_zenith
    solar_azimuth = irradiance.solar_azimuth
    solar_apparent_zenith = irradiance.solar_apparent_zenith
    dni = irradiance.DNI
    ghi = irradiance.GHI
    dhi = irradiance.DHI
    
    # Get the POA for this specific facade
    poa = pvlib.irradiance.get_total_irradiance(tilt, azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi)

    # Calculate the temperature of the cell
    temp_cell = pvlib.temperature.sapm_cell(poa.poa_global, temp_air, wind, module.A, module.B, module.DTC)
    
    # Calculate the relative and absolute airmass
    relative_airmass = pvlib.atmosphere.get_relative_airmass(solar_apparent_zenith)
    absolute_airmass = pvlib.atmosphere.get_absolute_airmass(relative_airmass)
    
    # Calculate the Angle of Incidence
    aoi = pvlib.irradiance.aoi(tilt, azimuth, solar_zenith, solar_azimuth)
    
    # Calculate the effective irradiance
    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(poa.poa_direct, poa.poa_diffuse, absolute_airmass, aoi, module)
    
    # Calculate the performance of the cell
    performance = pvlib.pvsystem.sapm(effective_irradiance, temp_cell, module)
    
    # Calculate the total and relative annual yield
    return {
        'dc': performance.p_mp,
        'ac': performance.p_mp.apply(get_ac_from_dc, args=(module.Wp,))
    }
