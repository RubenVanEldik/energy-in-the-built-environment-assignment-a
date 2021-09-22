# -*- coding: utf-8 -*-

import json
import pvlib
from utils import get_irradiance
from dataprep import get_knmi_data
from question1 import calculate_dni

LATITUDE = 53.224
LONGITUDE = 5.752

# Get the building info
buildings = json.load(open('../input/buildings.json', 'r'))

# Get the irradiance data from the KNMI data
filename = get_knmi_data()
irradiance = get_irradiance(filename, latitude=LATITUDE, longitude=LONGITUDE, index_col='datetime', temp_col='temp')

# Get the DNI and DHI
dirindex_dni = calculate_dni('dirindex', irradiance)
dirindex_dhi = irradiance.GHI - dirindex_dni

POA = pvlib.irradiance.get_total_irradiance(90, 225,
                                            irradiance.solar_zenith, irradiance.solar_azimuth,
                                            dirindex_dni, irradiance.GHI, dirindex_dhi, dni_extra=None, airmass=None,
                                            albedo=0.25, surface_type=None, model='isotropic',
                                            model_perez='allsitescomposite1990')
poa_val = POA
# Calculating POA question 2.3
# for building in buildings:
# for facade in building:
