import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
import json
import utils

def calculate_capacity(buildings):
    """
    Calculate the number of panels and total capacity of each facade per module type
    
    Parameters:
        buildings (obj): Original buildings object

    Returns:
        obj: Buildings object with capacity and number of panels per facade and module type
    """
    buildings = buildings.copy()
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
                    'capacity': num_panels * module.get('Wp')
                }
    return buildings


def calculate_power_output(buildings):
    """
    Calculate the DC and AC power output of each facade per module type
        
    Parameters:
        buildings (obj): Original buildings object

    Returns:
        obj: Buildings object with annual yield per facade and module type
    """
    buildings = buildings.copy()
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
                        
            # Add the number of panels and the total possible max capacity for all three modules
            for module_type in parameters:
                module = parameters[module_type]
                
                power_info = utils.pv.calculate_power_output(irradiance, module, tilt=facade['tilt'], azimuth=facade['azimuth'])

                # Calculate the annual yield and efficiency
                num_panels = facade[module_type]['num_panels']
                annual_yield_dc = num_panels * power_info['dc'].sum() / 1000
                annual_yield_ac = num_panels * power_info['ac'].sum() / 1000
                inverter_efficiency = annual_yield_ac / annual_yield_dc
                
                # Add the annual yield and efficiency to the tab
                facade[module_type].update({
                    'total_annual_yield_dc': annual_yield_dc,
                    'specific_annual_yield_dc': annual_yield_dc / facade['area'],
                    'total_annual_yield_ac': annual_yield_ac,
                    'specific_annual_yield_ac': annual_yield_ac / facade['area'],
                    'annual_inverter_efficiency': inverter_efficiency
                })
    return buildings


def find_best_module(facade):
    """
    Find the best module for specific facade

    Parameters:
        facade (obj): Data about the specific facade

    Returns:
        str: Name of the best module
    """
    best_module = None
    for module in parameters:
        if not best_module or facade[module]['total_annual_yield_dc'] > facade[best_module]['total_annual_yield_dc']:
            best_module = module
    return best_module

    
def create_bar_chart_for_all_modules(column, *, filename, ylabel):
    """
    Create a bar chart with all facades and modules
    
    Parameters:
        column (str): Name of column that should be plotted
        filename (str): Name under which file should be saved
        ylabe (str): Name of the vertical axis
    """
    facades_dataframe = pd.DataFrame({}, columns=parameters.columns.to_series())
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            facades_dataframe.loc[f'{building} - {facade_name}'] = list(map(lambda parameter : facade[parameter][column], parameters))
            
    facades_dataframe.plot(kind='bar', ylabel=ylabel)
    utils.plots.savefig(f'../output/question3/{filename}.png')


def create_bar_chart_for_best_module(column, *, filename, ylabel):
    """
    Create a bar chart for the best module for each facade
    
    Parameters:
        column (str): Name of column that should be plotted
        filename (str): Name under which file should be saved
        ylabe (str): Name of the vertical axis
    """
    facades_dataframe = pd.Series([], dtype='float64')
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
            best_module = find_best_module(facade)
            facades_dataframe.loc[f'{building} - {facade_name}'] = facade[best_module][column]
            
    facades_dataframe.plot(kind='bar', ylabel=ylabel)
    utils.plots.savefig(f'../output/question3/{filename}.png')


def create_line_chart_for_day(dates):
    """
    Create a line chart for the AC power output for the given dates
    
    Parameters:
        dates (list): List of dates that should be plotted
    """
    for building in buildings:
        # Create a new chart for each building
        figure, axes = utils.plots.create_plot_with_subplots(len(dates), 1, xlabel='Time [hour]', ylabel='Average output [$kW_{ac}$]', sharex=False)

        # Create a subplot for each day
        for index, date in enumerate(dates):
            power_per_facade = {}
            # Calculate the power output for each facade
            for facade_name in buildings[building]:
                # Save some variables
                facade = buildings[building][facade_name]
                best_module = find_best_module(facade)
                irradiance_day = irradiance.loc[date]
                
                # Calculate the power output and save it in the power_outputs dictionary
                ac_power = utils.pv.calculate_power_output(irradiance_day, parameters[best_module], tilt=facade['tilt'], azimuth=facade['azimuth'])['ac']
                power_per_facade[facade_name] = facade[best_module]['num_panels'] * ac_power / 1000
    
            # Create a subplot and plot a line for each subplot
            subplot = axes[index]
            subplot.title.set_text(datetime.datetime.strptime(date, '%Y-%m-%d').strftime("%B %d %Y"))
            subplot.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            for facade in power_per_facade:
                subplot.plot(power_per_facade[facade], label=facade)
            
            # Add a legend to only the top subplot
            if (index == 0):
                subplot.legend()

        # Save the chart
        building_name_lowercase = building.lower().replace(' ', '_')
        utils.plots.savefig(f'../output/question4/power_output_day_{building_name_lowercase}.png')
        plt.show()


def create_table_pv_systems():
    """
    Create a LaTeX table with info about each facade
    """
    facades = pd.DataFrame({}, columns=['Facade name', 'Best module', 'Total capacity', 'Tilt', 'Orientation'])
    for building in buildings:
        for facade_name in buildings[building]:
            facade = buildings[building][facade_name]
                            
            # Add the facade info to the facades DataFrame
            name = f'{building} - {facade_name}'
            best_module = find_best_module(facade)
            total_capacity = facade[best_module]['capacity']
            tilt = facade['tilt']
            orientation = facade['azimuth']
            facades.loc[name] = [name, best_module, total_capacity, tilt, orientation]
    
    # Create a LaTeX table from the DataFrame
    utils.files.save_text_file(facades.to_latex(), filepath='../output/question3/table_pv_systems.tex')


"""
This file answers both question 3 and 4.
    Question 3 calculates the DC performance for different panels and finds the best panel for each facade
    Question 4 calculates the AC performance each facade

Question 3 is answered in three steps:
1. Import data
    a. Building data with info on each facade
    b. Irradiance from the KNMI data set
    c. Module parameters
2. Calculate the capacity and power output per facade
3. Create output data
    a. Create a bar chart with the total annual yield DC
    b. Create a bar chart with the total annual yield AC
    c. Create a LaTeX table for all facades with the best module, capacity, tilt, and orientation
    
The calculations for question 4 are already done during question3, so only the figures have to be created
1. Create a bar chart for the total annual AC yield
2. Create a bar chart for the specific annual AC yield
3. Create a bar charter for the annual inverter efficiency
3. Create a line chart for average hourly AC output for three different days
"""

# Import data
irradiance = utils.knmi.get_irradiance()
buildings = json.load(open('../output/question2/buildings.json', 'r'))
parameters = pd.read_excel('../input/Module parameters.xlsx', index_col='Parameters')

# Calculate the capacity and power output per facade
buildings = calculate_capacity(buildings)
buildings = calculate_power_output(buildings)

# Create bar charts for the total and specific annual yield
create_bar_chart_for_all_modules('total_annual_yield_dc', filename='total_annual_yield_dc', ylabel='Total annual yield [$kWh_{dc} / year$]')
create_bar_chart_for_all_modules('total_annual_yield_ac', filename='total_annual_yield_ac', ylabel='Total annual yield [$kWh_{ac} / year$]')
create_table_pv_systems()

# Question 4
create_bar_chart_for_best_module('total_annual_yield_ac', filename='total_annual_yield_ac_best', ylabel='Total annual yield [$kWh_{ac} / year$]')
create_bar_chart_for_all_modules('specific_annual_yield_dc', filename='specific_annual_yield_dc', ylabel='Specific annual yield [$kWh_{dc} / m^2 year$]')
create_bar_chart_for_all_modules('annual_inverter_efficiency', filename='annual_inverter_efficiency', ylabel='Annual inverter efficiency')
create_line_chart_for_day(['2019-03-01', '2019-06-01', '2019-09-01'])

# Save the buildings info in a new JSON file
utils.files.save_json_file(buildings, filepath='../output/question3/buildings.json')
