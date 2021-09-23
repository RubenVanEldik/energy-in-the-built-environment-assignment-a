# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
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

def calculate_poa(tilt, azimuth, irradiance):
    """
    Calculate the total irradiance for a tilt, azimuth and irradiance

    Parameters:
        tilt (float or int): Tilt of surface
        azimuth (float or int): Azimuth of surface
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        obj: Object with total, diffuse, and direct irradiance data
    """
    # Define local variables for the get_total_irradiance function
    solar_zenith = irradiance.solar_zenith
    solar_azimuth = irradiance.solar_azimuth
    dni = irradiance.DNI
    ghi = irradiance.GHI
    dhi = irradiance.DHI
    
    poa = pvlib.irradiance.get_total_irradiance(tilt, azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi)
    return {
        'total': poa.poa_global.sum() / 1000,
        'diffuse': poa.poa_diffuse.sum() / 1000,
        'direct': poa.poa_direct.sum() / 1000
    }


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
            poa = calculate_poa(facade['tilt'], facade['azimuth'], irradiance)
            facade['poa_total'] = poa['total']
            facade['poa_diffuse'] = poa['diffuse']
            facade['poa_direct'] = poa['direct']
          
            
def find_best_orientation(irradiance, *, azimuths, tilts):
    """
    Calculate the total POA for different tilt angles

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        null
    """
    # Create a DataFrame with a double index (azimuth and tilt)
    index = [np.array(azimuths * 3), np.array(['total', 'diffuse', 'direct'] * len(azimuths))]
    poa_angles = pd.DataFrame(index=index)
    for azimuth in azimuths:
        for tilt in tilts:
            poa = calculate_poa(tilt, azimuth, irradiance)
            poa_angles.loc[(azimuth, tilt)] = [poa['total'], poa['diffuse'], poa['direct']]

    # Create the bar chart
    #fig = poa_angles.total.plot(kind='bar', ylabel='Total irradiance [kWh/m2 year]')
    #fig.set_xticklabels([f'{tilt} deg' for tilt in tilts], rotation=45)

        
get_poa_all_facades(buildings, irradiance)
find_best_orientation(irradiance, azimuths=[180], tilts=range(10, 45, 5))
find_best_orientation(irradiance, azimuths=[135, 225], tilts=range(10, 45, 5))