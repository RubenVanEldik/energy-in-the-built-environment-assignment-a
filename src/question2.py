# -*- coding: utf-8 -*-

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

           

# Calculating POA question 2.3
for building in buildings:
    for facade in building['facades']:
        POA = pvlib.irradiance.get_total_irradiance(facade['tilt'], facade['azimuth'], solar_zenith, solar_azimuth, dni, ghi, dhi, dni_extra=None, airmass=None, albedo=0.25, surface_type=None, model='isotropic', model_perez='allsitescomposite1990', **kwargs)
        print(POA)