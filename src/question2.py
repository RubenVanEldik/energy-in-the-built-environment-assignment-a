# -*- coding: utf-8 -*-

import json
import pvlib
import utils

LATITUDE = 53.224
LONGITUDE = 5.752

# Get the building info
buildings = json.load(open('../input/buildings.json', 'r'))

# Get the irradiance data from the KNMI data
filename = utils.get_knmi_data()
irradiance = utils.get_irradiance(filename, latitude=LATITUDE, longitude=LONGITUDE, index_col='datetime', temp_col='temp')

# Get the DNI and DHI
irradiance['DNI'] = utils.calculate_dni('dirindex', irradiance, latitude=LATITUDE, longitude=LONGITUDE)
irradiance['DHI'] = irradiance.GHI - irradiance.DNI

def get_poa_all_facades(buildings, irradiance):
    """
    Loop over all facades of all buildings and calculate the the irradiance for each hour

    Parameters:
        buildings (obj): Nested object with buildings and facades
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        null
    """
    for building in buildings:
        for facade in buildings[building]['facades']:
            # Define local variables for the get_total_irradiance function
            tilt = facade['tilt']
            azimuth = facade['azimuth']
            zenith = irradiance.solar_zenith
            azimuth = irradiance.solar_azimuth
            dni = irradiance.DNI
            ghi = irradiance.GHI
            dhi = irradiance.DHI
            
            poa = pvlib.irradiance.get_total_irradiance(tilt, azimuth, zenith, azimuth, dni, ghi, dhi)
            facade['poa_total'] = poa.poa_global.sum() / 1000
            facade['poa_diffuse'] = poa.poa_diffuse.sum() / 1000
            facade['poa_direct'] = poa.poa_direct.sum() / 1000
            
get_poa_all_facades(buildings, irradiance)