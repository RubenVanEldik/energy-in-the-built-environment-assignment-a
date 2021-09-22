# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import utils


# Define the location
LATITUDE = 52.08746136865645
LONGITUDE = 5.168080610130638
MODELS = ['disc', 'dirint', 'dirindex', 'erbs']


def create_plot(rows, columns, *, xlabel, ylabel):
    """
    Create a plot with rows x columns subplots and labels on the outer axes

    Parameters:
        rows (int): Number of rows
        columns (int): Number of columns
        xlabel (str): Label for the x-axis
        ylabel (str): Label for the y-axis

    Returns:
        figure: Created figure
        axes: Created axes
    """
    # Create a figure with subplots and set the correct spacing
    figure, axes = plt.subplots(
        nrows=rows, ncols=columns, sharex=True, sharey=True)
    figure.subplots_adjust(wspace=0.2, hspace=0.4)

    # Set the axes label
    for vertical_axe in axes:
        vertical_axe[0].set(ylabel=ylabel)
    for horizontal_axe in axes[len(axes) - 1]:
        horizontal_axe.set(xlabel=xlabel)

    # Return the created figure
    return figure, axes


def create_scatterplot(irradiance):
    """
    Create a scatter plot of measured DNI vs the computed DNI

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        null
    """
    figure, axes = create_plot(
        2, 2, xlabel='Measured DNI', ylabel='Computed DNI')

    for index, model in enumerate(MODELS):
        subplot = axes[index // 2][index % 2]
        subplot.scatter(irradiance.DNI, irradiance['dni_' + model], s=0.0001)
        subplot.title.set_text(model.upper())

        # Add a trend line
        subplot.plot([0, 1000], [0, 1000], color='black', linewidth=1)

    plt.savefig("../figures/part1/scatterplot.png", dpi=300)


def create_histogram(irradiance):
    """
    Create a histogram of the deviation

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance

    Returns:
        null
    """
    figure, axes = create_plot(2, 2, xlabel='Deviation', ylabel='Occurrances')

    for index, model in enumerate(MODELS):
        subplot = axes[index // 2][index % 2]

        # Get the DNI error series
        dni_measured = irradiance.DNI
        dni_calculated = irradiance['dni_' + model]
        dni_error = dni_calculated - dni_measured

        # Create a subplot and set the model as title
        subplot.hist(dni_error, log=True, bins=100)
        subplot.title.set_text(model.upper())
    plt.savefig("../figures/part1/histogram.png", dpi=300)


# Get the irradiance and position of the sun
irradiance = utils.get_irradiance('../input/Irradiance_2015_UPOT.csv', latitude=LATITUDE, longitude=LONGITUDE, temp_col='temp_air')

# Calculate the different DNI's
for model in MODELS:
    irradiance['dni_' + model] = utils.calculate_dni(model, irradiance, latitude=LATITUDE, longitude=LONGITUDE)
    errors = utils.compare_series(irradiance.DNI, irradiance['dni_' + model])
    utils.print_object(errors, name=model, uppercase=True)

# Create the plots
create_scatterplot(irradiance)
create_histogram(irradiance)
