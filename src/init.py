# -*- coding: utf-8 -*-

import pandas as pd
import pvlib
import numpy as np

# Define the location
LATITUDE = 52.08746136865645
LONGITUDE = 5.168080610130638

def calculate_dni(model, irradiance, solar_position):
    """Return a DNI series based on the model, irradiance, and solar position"""
    # Define important variables
    time = irradiance.index
    ghi = irradiance.GHI
    zenith = solar_position['zenith']
    apparant_zenith = solar_position['apparent_zenith']
    
    # Calculate and return the DNI for a specific type
    if model == 'disc':
        return pvlib.irradiance.disc(ghi, zenith, time).dni
    if model == 'dirint':
        return pvlib.irradiance.dirint(ghi, zenith, time)
    if model == 'dirindex':
        relative_airmass = pvlib.atmosphere.get_relative_airmass(apparant_zenith)
        absolute_airmass = pvlib.atmosphere.get_absolute_airmass(relative_airmass)
        linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(time, LATITUDE, LONGITUDE)
        clearsky = pvlib.clearsky.ineichen(apparant_zenith, absolute_airmass, linke_turbidity, perez_enhancement=True)
        return pvlib.irradiance.dirindex(ghi, clearsky['ghi'], clearsky['dni'], zenith=zenith, times=time)
    if model == 'erbs':
        return pvlib.irradiance.erbs(ghi, zenith, time).dni
    raise Exception('Invalid GHI-DNI model type')
    
def compare_dni(model, measured, calculated):
    """Print the RMSE, MBE, and MAE for two data series"""
    rmse = ((measured - calculated) ** 2).mean() ** 0.5
    mbe = (measured - calculated).mean()
    mae = abs(measured - calculated).mean()
    print('{} RMSE: {}, MBE: {}, MAE: {}'.format(model.upper().ljust(8), round(rmse, 1), round(mbe, 1), round(mae, 1)))

# Get the irradiance and position of the sun
irradiance = pd.read_csv('../input/Irradiance_2015_UPOT.csv', sep=";", index_col="timestamp", parse_dates=True)
solar_position = pvlib.solarposition.ephemeris(irradiance.index, LATITUDE, LONGITUDE, temperature=irradiance.temp_air)

# Calculate the different DNI's
for model in ['disc', 'dirint', 'dirindex', 'erbs']:
    dni_calculated = calculate_dni(model, irradiance, solar_position)
    dni_calculated.replace([np.inf, -np.inf], np.nan, inplace=True)
    compare_dni(model, irradiance.DNI, dni_calculated)
    