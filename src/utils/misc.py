from scipy import stats

def compare_series(series_a, series_b):
    """
    Calculate the RMSE, MBE, and MAE for two data series

    Parameters:
        series_a (Series): First pandas series
        series_b (Series): Second pandas series

    Returns:
        obj: Object with the 'rmse', 'mbe', 'mae', 'rsqr' values
    """
    return {
        'rmse': ((series_a - series_b) ** 2).mean() ** 0.5,
        'mbe': (series_a - series_b).mean(),
        'mae': abs(series_a - series_b).mean(),
        'rsqr': stats.linregress(series_a, series_b).rvalue ** 2
    }


def print_object(dict, *, name='', uppercase=False):
    """
    Print the values of an object nicely on a single line

    Parameters:
        dict (dict): Dictionary that should be printed
        name (string): Name that should appear before the first key/value of the dictionary
        uppercase (bool): Whether or not the keys should be printed in capital letters

    Returns:
        null
    """
    string = name.ljust(10) if name != '' else ''
    for key in dict:
        string += f'{key.upper() if uppercase else key}: {"" if dict[key] < 0 else " "}{float(dict[key]):.4}'.ljust(
            len(key) + 10)

    print(string)

