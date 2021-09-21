# -*- coding: utf-8 -*-
import pandas as pd
import pvlib
import dataprep
from init import calculate_dni
# Create 'table' with surface tilt and azimuth

buildings = {
    'House A': {
        'facades' : [{
                'tilt' : 90,
                'azimuth' : 225
            },
            {
                'tilt' : 90,
                'azitmuth' : 135
            }]
        },
    'House B': {
        'facades' : [{
                'tilt' : 90,
                'azimuth' : 270
            },
            {
                'tilt' : 90,
                'azitmuth' : 180
            },
            {
                'tilt' : 90,
                'azitmuth' : 90
            }]
        },
    'House C': {
        'facades' : [{
                'tilt' : 40,
                'azimuth' : 180
            }]
            },
    'House D': {
        'facades' : [{
                'tilt' : 40,
                'azimuth' : 270
            },
            {
                'tilt' : 40,
                'azitmuth' : 90
            }]
        }
        
    }

LATITUDE = 53.224
LONGITUDE = 5.752
file = dataprep.getKNMIdata()

print(file);
KNMIdata = pd.read_csv(file,
                         sep=";", index_col="datetime", parse_dates=True)

solar_position = pvlib.solarposition.ephemeris(
    KNMIdata.index, LATITUDE, LONGITUDE, temperature=KNMIdata.temp)           

dirindex_dni = calculate_dni('dirindex', KNMIdata, solar_position)

dirindex_dhi = KNMIdata['GHI'] - dirindex_dni

POA = pvlib.irradiance.get_total_irradiance(90, 225, 
                                            solar_position['zenith'], solar_position['azimuth'], 
                                            dirindex_dni, KNMIdata['GHI'], dirindex_dhi, dni_extra=None, airmass=None, 
                                            albedo=0.25, surface_type=None, model='isotropic', 
                                            model_perez='allsitescomposite1990')
poa_val = POA
print(POA)
# Calculating POA question 2.3
#for building in buildings:
    #for facade in building:
        
        