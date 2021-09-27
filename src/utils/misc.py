from scipy import stats


def compare_series(series_a, series_b):
    """
    Calculate the RMSE, MBE, and MAE for two data series.

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
        'rsqr': stats.linregress(series_a, series_b).rvalue ** 2,
    }


def print_object(dict_to_print, *, name='', uppercase=False):
    """
    Print the values of an object nicely on a single line.

    Parameters:
        dict (dict): Dictionary that should be printed
        name (string): Name that should appear before the first key/value of the dictionary
        uppercase (bool): Whether or not the keys should be printed in capital letters
    """
    string = '' if name == '' else name.ljust(10)
    for key, value in dict_to_print.items():
        string += f'{key.upper() if uppercase else key}: {"" if value < 0 else " "}{float(value):.4}'.ljust(
            len(key) + 10)

    print(string)
