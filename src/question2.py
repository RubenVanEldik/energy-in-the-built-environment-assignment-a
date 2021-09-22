# -*- coding: utf-8 -*-

import json
import pandas as pd
import pvlib
from dataprep import get_knmi_data

buildings = json.load(open('../input/buildings.json', 'r'))
from question1 import calculate_dni

LATITUDE = 53.224
LONGITUDE = 5.752

file = get_knmi_data()

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
# for building in buildings:
# for facade in building:
