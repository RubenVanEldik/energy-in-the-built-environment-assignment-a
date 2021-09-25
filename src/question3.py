# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 16:35:32 2021

@author: Marita
"""

import pandas as pd
import math
import json
import utils

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
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
                        
            # Add the number of panels and the total possible max capacity for all three modules
            for module_type in parameters:
                module = parameters[module_type]
                
                power_info = utils.calculate_power_output(irradiance, module, tilt=facade['tilt'], azimuth=facade['azimuth'])

                num_panels = facade[module_type]['num_panels']
                annual_yield_dc = num_panels * power_info['dc'].sum() / 1000
                annual_yield_ac = num_panels * power_info['ac'].sum() / 1000
                facade[module_type]['total_annual_yield_dc'] = annual_yield_dc
                facade[module_type]['specific_annual_yield_dc'] = annual_yield_dc / facade['area']
                facade[module_type]['total_annual_yield_ac'] = annual_yield_ac
                facade[module_type]['specific_annual_yield_ac'] = annual_yield_ac / facade['area']
                facade[module_type]['annual_inverter_efficiency'] = facade[module_type]['total_annual_yield_ac'] / facade[module_type]['total_annual_yield_dc'] 
    
    
def create_bar_chart_for_facades_and_modules(column, *, filename, ylabel):
    """
    Create a bar chart with the total POA for each facade
    """
    facades_dataframe = pd.DataFrame({}, columns=parameters.columns.to_series())
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            facades_dataframe.loc[f'{building} - {facade_name}'] = list(map(lambda parameter : facade[parameter][column], parameters))
            
    facades_dataframe.plot(kind='bar', ylabel=ylabel)
    utils.savefig(f'../output/question3/{filename}.png')


def create_table_pv_systems():
    facades = pd.DataFrame({}, columns=['Facade name', 'Best module', 'Total capacity', 'Tilt', 'Orientation'])
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            
            # Find the best module for specific facade
            best_module = None
            for module in parameters:
                if not best_module or facade[module]['total_annual_yield_dc'] > facade[best_module]['total_annual_yield_dc']:
                    best_module = module
                
            # Add the facade info to the facades DataFrame
            name = f'{building} - {facade_name}'
            total_capacity = facade[best_module]['possible_capacity']
            tilt = facade['tilt']
            orientation = facade['azimuth']
            facades.loc[name] = [name, best_module, total_capacity, tilt, orientation]
    
    # Create a LaTeX table from the DataFrame
    utils.save_text_file(facades.to_latex(), filepath='../output/question3/table_pv_systems.tex')


calculate_possible_capacity()
calculate_dc_power()

# Create bar charts for the total and specific annual yield
create_bar_chart_for_facades_and_modules('total_annual_yield_dc', filename='total_annual_yield_dc', ylabel='Total annual yield [$kWh_{dc} / year$]')
create_bar_chart_for_facades_and_modules('total_annual_yield_ac', filename='total_annual_yield_ac', ylabel='Total annual yield [$kWh_{ac} / year$]')
create_table_pv_systems()

# Question 4
create_bar_chart_for_facades_and_modules('specific_annual_yield_dc', filename='specific_annual_yield_dc', ylabel='Specific annual yield [$kWh_{dc} / m^2 year$]')
create_bar_chart_for_facades_and_modules('annual_inverter_efficiency', filename='annual_inverter_efficiency', ylabel='Annual inverter efficiency')

# Save the buildings info in a new JSON file
utils.save_json_file(buildings, filepath='../input/buildings_processed_q3.json')
