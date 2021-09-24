# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 16:35:32 2021

@author: Marita
"""

import pandas as pd
import math
import json
import utils
import pvlib

irradiance = utils.get_knmi_irradiance()
parameters = pd.read_excel('../input/Module parameters.xlsx', index_col='Parameters')
buildings = json.load(open('../input/buildings_processed_q2.json', 'r'))

def calculate_possible_capacity():
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            
            # Calculate the possible installation area
            installation_area = facade['area'] * facade['coverage']
            
            # Add the number of panels and the total possible max capacity for all three modules
            for module_type in parameters:
                module = parameters[module_type]
                facade[f'panels_{module_type}'] = math.floor(installation_area / module.get('Area'))
                facade[f'possible_capacity_{module_type}'] = facade[f'panels_{module_type}'] * module.get('Wp')


def calculate_dc_power():
    wind = irradiance.wind
    temp_air = irradiance.temp
    solar_zenith = irradiance.solar_zenith
    solar_azimuth = irradiance.solar_azimuth
    solar_apparent_zenith = irradiance.solar_apparent_zenith
    dni = irradiance.DNI
    ghi = irradiance.GHI
    dhi = irradiance.DHI
    
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
                        
            # Add the number of panels and the total possible max capacity for all three modules
            for module_type in parameters:
                module = parameters[module_type]
                
                # Get the POA for this specific facade
                poa = pvlib.irradiance.get_total_irradiance(facade['tilt'], facade['azimuth'], solar_zenith, solar_azimuth, dni, ghi, dhi)

                # Calculate the temperature of the cell
                temp_cell = pvlib.temperature.sapm_cell(poa.poa_global, temp_air, wind, module.A, module.B, module.DTC)
                
                # Calculate the relative and absolute airmass
                relative_airmass = pvlib.atmosphere.get_relative_airmass(solar_apparent_zenith)
                absolute_airmass = pvlib.atmosphere.get_absolute_airmass(relative_airmass)
                
                # Calculate the Angle of Incidence
                aoi = pvlib.irradiance.aoi(facade['tilt'], facade['azimuth'], solar_zenith, solar_azimuth)
                
                # Calculate the effective irradiance
                effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(poa.poa_direct, poa.poa_diffuse, absolute_airmass, aoi, module)
                
                # Calculate the performance of the cell
                performance = pvlib.pvsystem.sapm(effective_irradiance, temp_cell, module)
                
                # Calculate the total and relative annual yield
                num_panels = facade[f'panels_{module_type}']
                facade[f'total_annual_yield_{module_type}'] = num_panels * performance.p_mp.sum() / 1000
                facade[f'relative_annual_yield_{module_type}'] = facade[f'total_annual_yield_{module_type}'] / facade['area']
    
calculate_possible_capacity()
calculate_dc_power()

# Save the buildings info in a new JSON file
utils.save_json_file(buildings, filepath='../input/buildings_processed_q3.json')
