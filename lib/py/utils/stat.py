import math
import numpy as np


def get_cdf(data):
    ''' Calculating CDF of some data

    Args:
        data: A list of numbers

    Returns:
        (x, y):
            x is a list containing the x values
            y is a list containing the probabilities
                y[i] = P(x <= x[i])
    '''
    data_sorted = np.sort(data)
    n = len(data)
    prob = np.arange(1, n + 1) / n
    return data_sorted, prob


def get_percentile(data, percentile):
    ''' Get the percentile of some data

    Args:
        data: A list of numbers

    Returns:
        The percentile of data
    '''
    print(
        'DEPRECATED. Recommnend to use'
        '`dataframe.quantile(0.99, interpolation=lower)` instead'
    )
    data_sorted = np.sort(data)
    n = len(data)
    pos = math.floor(percentile * n) - 1
    pos = max(0, pos)
    return data_sorted[pos]


def get_fairness_index(data):
    ''' Get Jain's fairness index

    Args:
        data: A list of numbers

    Returns:
        A floating number representing Jain's fairness index
    '''
    data = np.array(data)
    return (data.mean())**2 / (data**2).mean()
