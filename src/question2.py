"""
Question 2 calculates the POA (plane of irradiance) for each of the four building surfaces.

This is done in four steps:
1. Import data
    a. Building data with info on each facade
    b. Irradiance from the KNMI data set
2. Find the best orientation for the solar panels on rooftop A and B    
    a. Calculate the POA for each position
    b. Create a bar chart for the POA irradiance of all positions
    c. Find the optimal position
3. Calculate the POA for all facades and save the extended building info to a JSON file
4. Create a bar chart of the POA of all surfaces
"""

import pandas as pd
import math
import pvlib
from matplotlib import pyplot as plt

import utils

COLORS = ['#aa3026', '#91723c', '#915a8d', '#85ab7b']


def calculate_poa(tilt, azimuth, irradiance):
    """
    Calculate the total irradiance for a tilt, azimuth and irradiance.

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
    relative_airmass = pvlib.atmosphere.get_relative_airmass(
        irradiance.solar_apparent_zenith)

    poa = pvlib.irradiance.get_total_irradiance(
        tilt, azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi, airmass=relative_airmass)
    return {
        'total': poa.poa_global.sum() / 1000,
        'diffuse': poa.poa_diffuse.sum() / 1000,
        'direct': poa.poa_direct.sum() / 1000,
    }


def find_best_orientation(irradiance, *, azimuths, tilts, plotname):
    """
    Calculate the total POA for different tilt angles.

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        obj: Object with the optimal tilt and azimuth
    """
    # Create a DataFrame with the azimuths as columns
    all_orientations = pd.DataFrame(columns=azimuths)

    # Loop over all the tilts and add a row with the total POA for each azimuth
    for tilt in tilts:
        all_orientations.loc[tilt] = list(map(lambda azimuth: calculate_poa(
            tilt, azimuth, irradiance)['total'], azimuths))

    # Find and return the optimal azimuth and tilt in the DataFrame
    optimal_azimuth = all_orientations.max().idxmax()
    optimal_tilt = all_orientations[optimal_azimuth].idxmax()

    # Create and save the bar chart
    fig = all_orientations.plot(
        kind='bar', xlabel='Tilt [deg]', ylabel='Total irradiance [$kWh/m^2 year$]', color=COLORS)
    fig.legend(title='Azimuth [deg]', loc=4)

    max_value = all_orientations.loc[optimal_tilt, optimal_azimuth]
    fig.set_ylim([1100, math.ceil(max_value / 20) * 20])
    utils.plots.savefig(f'../output/question2/{plotname}.png')
    plt.show()

    return {'tilt': int(optimal_tilt), 'azimuth': int(optimal_azimuth)}


def get_poa_all_facades(buildings, irradiance):
    """
    Loop over all facades of all buildings and calculate the the irradiance for each hour.

    Parameters:
        buildings (obj): Nested object with buildings and facades
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        obj: Buildings object with the POA info per facade
    """
    buildings = buildings.copy()
    for building in buildings.values():
        for facade in building.values():
            poa = calculate_poa(facade['tilt'], facade['azimuth'], irradiance)
            facade.update({
                'poa_total': poa['total'],
                'poa_diffuse': poa['diffuse'],
                'poa_direct': poa['direct'],
            })
    return buildings


def create_poa_bar_chart():
    """
    Create a bar chart with the total POA for each facade.
    """
    all_poas = pd.Series([], dtype='float64')
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            all_poas.loc[f'{building} - {facade_name}'] = facade['poa_total']

    all_poas.plot(kind='bar', ylabel='Total irradiance [$kWh/m^2 year$]')
    utils.plots.savefig('../output/question2/poa_all_facades.png')


# Get the building and KNMI irradiance data
buildings = utils.files.open_json_file('../input/buildings.json')
irradiance = utils.knmi.get_irradiance()

# Find the best orientation for the panels on rooftop A and B
orientation_rooftop_b = find_best_orientation(
    irradiance, plotname='rooftop_b', tilts=range(10, 45, 5), azimuths=[180])
orientation_rooftop_a = find_best_orientation(
    irradiance, plotname='rooftop_a', tilts=range(10, 45, 5), azimuths=[135, 225])
buildings['House A']['Rooftop'] = {
    **orientation_rooftop_a, 'area': 3000, 'coverage': 0.5}
buildings['House B']['Rooftop'] = {
    **orientation_rooftop_b, 'area': 1500, 'coverage': 0.5}

# Calculate the POA for all facades and save the extended building info to a JSON file
buildings = get_poa_all_facades(buildings, irradiance)
utils.files.save_json_file(
    buildings, filepath='../output/question2/buildings.json')

# Create a bar chart of the POA of all surfaces
create_poa_bar_chart()
