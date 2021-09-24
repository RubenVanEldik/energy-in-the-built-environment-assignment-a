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
                num_panels = math.floor(installation_area / module.get('Area'))
                facade[module_type] = {
                    'num_panels': num_panels,
                    'possible_capacity': num_panels * module.get('Wp')
                }


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
                num_panels = facade[module_type]['num_panels']
                facade[module_type]['total_annual_yield'] = num_panels * performance.p_mp.sum() / 1000
                facade[module_type]['specific_annual_yield'] = facade[module_type]['total_annual_yield'] / facade['area']
    
    
def create_annual_yield_bar_chart(column, *, filename, ylabel):
    """
    Create a bar chart with the total POA for each facade
    """
    facades_dataframe = pd.DataFrame({}, columns=parameters.columns.to_series())
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            facades_dataframe.loc[f'{building} - {facade_name}'] = list(map(lambda parameter : facade[parameter][column], parameters))
            
    facades_dataframe.plot(kind='bar', ylabel=ylabel)
    utils.savefig(f'../figures/question3/{filename}.png')


def create_table_pv_systems():
    facades = pd.DataFrame({}, columns=['Facade name', 'Best module', 'Total capacity', 'Tilt', 'Orientation'])
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            
            # Find the best module for specific facade
            best_module = None
            for module in parameters:
                if not best_module or facade[module]['total_annual_yield'] > facade[best_module]['total_annual_yield']:
                    best_module = module
                
            # Add the facade info to the facades DataFrame
            name = f'{building} - {facade_name}'
            total_capacity = facade[best_module]['possible_capacity']
            tilt = facade['tilt']
            orientation = facade['azimuth']
            facades.loc[name] = [name, best_module, total_capacity, tilt, orientation]
    
    # Create a LaTeX table from the DataFrame
    print(facades.to_latex())


calculate_possible_capacity()
calculate_dc_power()

# Create bar charts for the total and specific annual yield
create_annual_yield_bar_chart('total_annual_yield', filename='total_annual_yield', ylabel='Total annual yield [$kWh / year$]')
create_annual_yield_bar_chart('specific_annual_yield', filename='specific_annual_yield', ylabel='Specific annual yield [$kWh / m^2 year$]')
create_table_pv_systems()

# Save the buildings info in a new JSON file
utils.save_json_file(buildings, filepath='../input/buildings_processed_q3.json')
