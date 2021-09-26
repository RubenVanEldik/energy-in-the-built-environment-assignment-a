import utils

# Define the location and the models to use
LATITUDE = 52.08746136865645
LONGITUDE = 5.168080610130638
MODELS = ['disc', 'dirint', 'dirindex', 'erbs']


def create_measured_vs_calculated_scatterplot(irradiance):
    """
    Create a scatter plot of measured DNI vs the computed DNI

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance
    """
    xlabel = 'Measured DNI [$W/m^2$]'
    ylabel = 'Computed DNI [$W/m^2$]'
    figure, axes = utils.plots.create_plot_with_subplots(2, 2, xlabel=xlabel, ylabel=ylabel)

    for index, model in enumerate(MODELS):
        subplot = axes[index // 2][index % 2]
        subplot.scatter(irradiance.DNI, irradiance['dni_' + model], s=0.00005)
        subplot.title.set_text(model.upper())

        # Add a trend line
        subplot.plot([0, 1000], [0, 1000], color='black', linewidth=1)

    utils.plots.savefig('../output/question1/measured_vs_calculated_scatterplot.png')


def create_elevation_vs_error_scatterplot(irradiance):
    """
    Create a scatter plot of the solar elevation vs DNI error

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance
    """
    figure, axes = utils.plots.create_plot_with_subplots(
        2, 2, xlabel='Solar elevation [deg]', ylabel='DNI error [$W/m^2$]')

    for index, model in enumerate(MODELS):
        dni_measured = irradiance.DNI
        dni_calculated = irradiance['dni_' + model]
        dni_error = dni_calculated - dni_measured

        subplot = axes[index // 2][index % 2]
        subplot.scatter(irradiance['solar_elevation'], dni_error, s=0.00005)
        subplot.title.set_text(model.upper())

    utils.plots.savefig('../output/question1/elevation_vs_error_scatterplot.png')


def create_histogram(irradiance):
    """
    Create a histogram of the deviation

    Parameters:
        irradiance (DataFrame): DataFrame with the irradiance
    """
    figure, axes = utils.plots.create_plot_with_subplots(2, 2, xlabel='DNI error [$W/m^2$]', ylabel='Occurrances [#]')

    for index, model in enumerate(MODELS):
        subplot = axes[index // 2][index % 2]

        # Get the DNI error series
        dni_measured = irradiance.DNI
        dni_calculated = irradiance['dni_' + model]
        dni_error = dni_calculated - dni_measured

        # Create a subplot and set the model as title
        subplot.hist(dni_error, log=True, bins=100)
        subplot.title.set_text(model.upper())
    utils.plots.savefig('../output/question1/histogram.png')


"""
The goal of question 1 is to find out which model is best in predicting the DNI for this specific location.

This is done in three steps:
1. Get the irradiance and solar position data
2. For each model
    a. Calculate the DNI
    b. Calculate the RMSE, MBE, MAE, and R2
3. Create plots with subplots for each model:
    a. Measured DNI vs. Calculated DNI
    b. Solar elevation vs. DNI error
    c. Histogram of the DNI error
"""

# Get the irradiance and position of the sun
irradiance = utils.pv.get_irradiance('../input/upot.csv', latitude=LATITUDE, longitude=LONGITUDE, temp_col='temp_air')

# Calculate the different DNI's
for model in MODELS:
    irradiance['dni_' + model] = utils.pv.calculate_dni(model, irradiance, latitude=LATITUDE, longitude=LONGITUDE)
    errors = utils.misc.compare_series(irradiance.DNI, irradiance['dni_' + model])
    utils.misc.print_object(errors, name=model, uppercase=True)

# Create the plots
create_measured_vs_calculated_scatterplot(irradiance)
create_elevation_vs_error_scatterplot(irradiance)
create_histogram(irradiance)
