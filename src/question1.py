# -*- coding: utf-8 -*-

import utils


# Define the location
LATITUDE = 52.08746136865645
LONGITUDE = 5.168080610130638
MODELS = ['disc', 'dirint', 'dirindex', 'erbs']


def create_measured_vs_calculated_scatterplot(irradiance):
    """
    Create a scatter plot of measured DNI vs the computed DNI

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        null
    """
    figure, axes = utils.create_plot_with_subplots(
        2, 2, xlabel='Measured DNI [$W/m^2$]', ylabel='Computed DNI [$W/m^2$]')

    for index, model in enumerate(MODELS):
        subplot = axes[index // 2][index % 2]
        subplot.scatter(irradiance.DNI, irradiance['dni_' + model], s=0.00005)
        subplot.title.set_text(model.upper())

        # Add a trend line
        subplot.plot([0, 1000], [0, 1000], color='black', linewidth=1)

    utils.savefig('../output/question1/measured_vs_calculated_scatterplot.png')
    
def create_elevation_vs_error_scatterplot(irradiance):
    """
    Create a scatter plot of the solar elevation vs DNI error

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        null
    """
    figure, axes = utils.create_plot_with_subplots(
        2, 2, xlabel='Solar elevation [deg]', ylabel='DNI error [$W/m^2$]')

    for index, model in enumerate(MODELS):
        dni_measured = irradiance.DNI
        dni_calculated = irradiance['dni_' + model]
        dni_error = dni_calculated - dni_measured

        subplot = axes[index // 2][index % 2]
        subplot.scatter(irradiance['solar_elevation'], dni_error, s=0.00005)
        subplot.title.set_text(model.upper())

    utils.savefig('../output/question1/elevation_vs_error_scatterplot.png')


def create_histogram(irradiance):
    """
    Create a histogram of the deviation

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        null
    """
    figure, axes = utils.create_plot_with_subplots(2, 2, xlabel='DNI error [$W/m^2$]', ylabel='Occurrances [#]')

    for index, model in enumerate(MODELS):
        subplot = axes[index // 2][index % 2]

        # Get the DNI error series
        dni_measured = irradiance.DNI
        dni_calculated = irradiance['dni_' + model]
        dni_error = dni_calculated - dni_measured

        # Create a subplot and set the model as title
        subplot.hist(dni_error, log=True, bins=100)
        subplot.title.set_text(model.upper())
    utils.savefig('../output/question1/histogram.png')


# Get the irradiance and position of the sun
irradiance = utils.get_irradiance('../input/Irradiance_2015_UPOT.csv', latitude=LATITUDE, longitude=LONGITUDE, temp_col='temp_air')

# Calculate the different DNI's
for model in MODELS:
    irradiance['dni_' + model] = utils.calculate_dni(model, irradiance, latitude=LATITUDE, longitude=LONGITUDE)
    errors = utils.compare_series(irradiance.DNI, irradiance['dni_' + model])
    utils.print_object(errors, name=model, uppercase=True)

# Create the plots
create_measured_vs_calculated_scatterplot(irradiance)
create_elevation_vs_error_scatterplot(irradiance)
create_histogram(irradiance)
