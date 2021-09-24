# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 16:35:32 2021

@author: Marita
"""

import pandas as pd
import math
import json

parameters = pd.read_excel('../input/Module parameters.xlsx', index_col='Parameters')
buildings = json.load(open('../input/buildings_processed.json', 'r'))

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


calculate_possible_capacity()