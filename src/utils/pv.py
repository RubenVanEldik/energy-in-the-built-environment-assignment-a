import pandas as pd
import pvlib

def get_irradiance(filename, *, latitude, longitude, index_col='timestamp', temp_col):
    """
    Get the irradiance and position of the sun and merge this with the original DataFrame

    Parameters:
        filename (string): Name of the CSV file with the irradiance data
        latitude (float): Latitude
        longitude (float): Longitude
        index_col (string): Name of the column that should be used as index (default is timestamp)
        temp_col (string): Name of the column with the temperature 

    Returns:
        DataFrame: A concatenated DataFrame of the input file with the solar info, the solar info columns start with 'solar_'
    """
    # TODO: check if dataset exists in UTC timezone.
    irradiance = pd.read_csv(filename,
                             sep=";", index_col=index_col, parse_dates=True)
    solar_position = pvlib.solarposition.ephemeris(
        irradiance.index, latitude, longitude, temperature=irradiance[temp_col])

    for column in solar_position:
        new_column_name = column if column.startswith(
            'solar') else f'solar_{column}'
        irradiance[new_column_name] = solar_position[column]

    # Remove all timestamps where the solar elevation is less than 4
    return irradiance[irradiance.solar_elevation > 4]


def calculate_dni(model, irradiance, *, latitude, longitude):
    """
    Calculate the DNI based on the model, irradiance, and solar position

    Parameters:
        model (string): The name of the model, has to be either 'disc', 'dirint', 'dirindex', or 'erbs'
        irradiance (DataFrame): DataFrame with all weather and irradiance data

    Returns:
        Series: The DNI series
    """
    # Define important variables
    time = irradiance.index
    ghi = irradiance.GHI
    zenith = irradiance['solar_zenith']
    apparent_zenith = irradiance['solar_apparent_zenith']

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
            time, latitude, longitude)
        clearsky = pvlib.clearsky.ineichen(
            apparent_zenith, absolute_airmass, linke_turbidity, perez_enhancement=True)
        return pvlib.irradiance.dirindex(ghi, clearsky['ghi'], clearsky['dni'], zenith=zenith, times=time)
    if model == 'erbs':
        return pvlib.irradiance.erbs(ghi, zenith, time).dni
    raise Exception('Invalid GHI-DNI model type')


def get_ac_from_dc(p_dc, p_ac0, *, efficiency_nom=0.96):
    """
    Calculate AC power output of the inverter for a specific DC power

    Parameters:
        p_dc (float or int): The DC power of the solar panels
        p_ac0 (float or int): Rated power of the inverter, equal to the rated DC power of the PV system

    Returns:
        float: The efficiency of the inverter
    """
    # Return 0 if the DC power is 0
    if p_dc == 0:
        return 0

    # Calculate the rated DC power and zeta
    p_dc0 = p_ac0 / efficiency_nom
    zeta = p_dc / p_dc0
    
    # Return the rated power of the inverter if the DC power is larger or equal to the rated DC power
    if p_dc >= p_dc0:
        return p_ac0

    # Calculate the efficiency
    efficiency = -0.0162 * zeta - (0.0059 / zeta) + 0.9858

    # Return the efficiency of the inverter times the DC power
    return efficiency * p_dc


def calculate_power_output(irradiance, module, *, tilt, azimuth):
    """
    Calculate DC and AC power output for each irradiance timestep

    Parameters:
        irradiance (DataFrame): DataFrame with all weather and irradiance data
        module (object): Parameters of the solar panel module
        tilt (float or int): Tilt angle of the panel (degrees)
        azimuth (float or int): Azimuth angle of the panel (degrees)

    Returns:
        obj: DC and AC power output for each irradiance timestep
    """
    # Define some variables
    wind = irradiance.wind
    temp_air = irradiance.temp
    solar_zenith = irradiance.solar_zenith
    solar_azimuth = irradiance.solar_azimuth
    solar_apparent_zenith = irradiance.solar_apparent_zenith
    dni = irradiance.DNI
    ghi = irradiance.GHI
    dhi = irradiance.DHI
    
    # Get the POA for this specific facade
    poa = pvlib.irradiance.get_total_irradiance(tilt, azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi)

    # Calculate the temperature of the cell
    temp_cell = pvlib.temperature.sapm_cell(poa.poa_global, temp_air, wind, module.A, module.B, module.DTC)
    
    # Calculate the relative and absolute airmass
    relative_airmass = pvlib.atmosphere.get_relative_airmass(solar_apparent_zenith)
    absolute_airmass = pvlib.atmosphere.get_absolute_airmass(relative_airmass)
    
    # Calculate the Angle of Incidence
    aoi = pvlib.irradiance.aoi(tilt, azimuth, solar_zenith, solar_azimuth)
    
    # Calculate the effective irradiance
    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(poa.poa_direct, poa.poa_diffuse, absolute_airmass, aoi, module)
    
    # Calculate the performance of the cell
    performance = pvlib.pvsystem.sapm(effective_irradiance, temp_cell, module)
    
    # Calculate the total and relative annual yield
    return {
        'dc': performance.p_mp,
        'ac': performance.p_mp.apply(get_ac_from_dc, args=(module.Wp,))
    }