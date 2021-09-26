# -*- coding: utf-8 -*-

import json
import pandas as pd
import matplotlib.pyplot as plt
import pvlib
import utils

# Get the building info
buildings = json.load(open('../input/buildings.json', 'r'))

irradiance = utils.knmi.get_knmi_irradiance()


def calculate_poa(tilt, azimuth, irradiance):
    """
    Calculate the total irradiance for a tilt, azimuth and irradiance

    Parameters:
        tilt (float or int): Tilt of surface
        azimuth (float or int): Azimuth of surface
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        obj: Object with total, diffuse, and direct irradiance data (in kWh)
    """
    # Define local variables for the get_total_irradiance function
    solar_zenith = irradiance.solar_zenith
    solar_azimuth = irradiance.solar_azimuth
    dni = irradiance.DNI
    ghi = irradiance.GHI
    dhi = irradiance.DHI
    relative_airmass = pvlib.atmosphere.get_relative_airmass(irradiance.solar_apparent_zenith)

    poa = pvlib.irradiance.get_total_irradiance(tilt, azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi, airmass=relative_airmass)
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
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            poa = calculate_poa(facade['tilt'], facade['azimuth'], irradiance)
            facade['poa_total'] = poa['total']
            facade['poa_diffuse'] = poa['diffuse']
            facade['poa_direct'] = poa['direct']


def find_best_orientation(irradiance, *, azimuths, tilts=range(10, 45, 5), plotname):
    """
    Calculate the total POA for different tilt angles

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        obj: Object with the optimal tilt and azimuth
    """
    # Create a DataFrame with the azimuths as columns
    all_orientations = pd.DataFrame(columns=azimuths)

    # Loop over all the tilts and add a row with the total POA for each azimuth
    for tilt in tilts:
        all_orientations.loc[tilt] = list(map(lambda azimuth : calculate_poa(tilt, azimuth, irradiance)['total'], azimuths))

    # Create and save the bar chart
    fig = all_orientations.plot(kind='bar', xlabel='Tilt [deg]', ylabel='Total irradiance [$kWh/m^2 year$]')
    fig.legend(title='Azimuth [deg]', loc=4)
    utils.plots.savefig(f'../output/question2/{plotname}.png')
    plt.show()

    # Find and return the optimal azimuth and tilt in the DataFrame
    optimal_azimuth = all_orientations.max().idxmax()
    optimal_tilt = all_orientations[optimal_azimuth].idxmax()
    return { 'tilt': int(optimal_tilt), 'azimuth': int(optimal_azimuth) }

def create_poa_bar_chart():
    """
    Create a bar chart with the total POA for each facade
    """
    all_poas = pd.Series([], dtype='float64')
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            all_poas.loc[f'{building} - {facade_name}'] = facade['poa_total']
            
    all_poas.plot(kind='bar', ylabel='Total irradiance [$kWh/m^2 year$]')
    utils.plots.savefig('../output/question2/poa_all_facades.png')


# Find the best orientation for the panels on rooftop A and B
orientation_rooftop_b = find_best_orientation(irradiance, plotname='rooftop_b', azimuths=[180])
orientation_rooftop_a = find_best_orientation(irradiance, plotname='rooftop_a', azimuths=[135, 225])
buildings['House A']['Rooftop'] = { **orientation_rooftop_a, 'area': 3000, 'coverage': 0.5 }
buildings['House B']['Rooftop'] = { **orientation_rooftop_b, 'area': 1500, 'coverage': 0.5 }

# Calculate the POA for all facades and save the extended building info to a JSON file
get_poa_all_facades(buildings, irradiance)
utils.files.save_json_file(buildings, filepath='../output/question2/buildings.json')

# Create a bar chart of the POA of all surfaces
create_poa_bar_chart()
