# -*- coding: utf-8 -*-

import pandas as pd
import pvlib
import numpy as np
import matplotlib.pyplot as plt
import utils

# Increase the padding between subplots
plt.subplots_adjust(wspace=0.4, hspace=0.4)

# Define the location
LATITUDE = 52.08746136865645
LONGITUDE = 5.168080610130638
MODELS = ['disc', 'dirint', 'dirindex', 'erbs']

def calculate_dni(model, irradiance, solar_position):
    """Return a DNI series based on the model, irradiance, and solar position"""
    # Define important variables
    time = irradiance.index
    ghi = irradiance.GHI
    zenith = solar_position['zenith']
    apparent_zenith = solar_position['apparent_zenith']

    # Calculate and return the DNI for a specific type
    if model == 'disc':
        return pvlib.irradiance.disc(ghi, zenith, time).dni
    if model == 'dirint':
        return pvlib.irradiance.dirint(ghi, zenith, time)
    if model == 'dirindex':
        relative_airmass = pvlib.atmosphere.get_relative_airmass(
            apparent_zenith)
        absolute_airmass = pvlib.atmosphere.get_absolute_airmass(
            relative_airmass)
        linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(
            time, LATITUDE, LONGITUDE)
        clearsky = pvlib.clearsky.ineichen(
            apparent_zenith, absolute_airmass, linke_turbidity, perez_enhancement=True)
        return pvlib.irradiance.dirindex(ghi, clearsky['ghi'], clearsky['dni'], zenith=zenith, times=time)
    if model == 'erbs':
        return pvlib.irradiance.erbs(ghi, zenith, time).dni
    raise Exception('Invalid GHI-DNI model type')

def create_histogram(irradiance):
    for index, model in enumerate(MODELS):
        # Get the DNI error series
        dni_measured = irradiance.DNI
        dni_calculated = irradiance['dni_' + model]
        dni_error = dni_calculated - dni_measured

        # Create a subplot and set the model as title
        plt.subplot(2, 2, index + 1)
        ax = dni_error.plot(kind='hist', logy=True, bins=100)
        ax.title.set_text(model)

# Get the irradiance and position of the sun
# TODO: check if dataset exists in UTC timezone.
irradiance = pd.read_csv('../input/Irradiance_2015_UPOT.csv',
                         sep=";", index_col="timestamp", parse_dates=True)
solar_position = pvlib.solarposition.ephemeris(
    irradiance.index, LATITUDE, LONGITUDE, temperature=irradiance.temp_air)

# Remove all timestamps where the solar elevation is less than 4
solar_position = solar_position[solar_position.elevation > 4]
irradiance = irradiance[irradiance.index.isin(solar_position.index)]

# Calculate the different DNI's
for model in MODELS:
    irradiance['dni_' + model] = calculate_dni(model, irradiance, solar_position)
    errors = utils.compare_series(irradiance.DNI, irradiance['dni_' + model])
    utils.print_object(errors, name=model, uppercase=True)
    

create_histogram(irradiance)