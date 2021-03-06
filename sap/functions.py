

import numpy as np


def gaussian(x, A, mu, sig):
    return A * np.exp(-(x - mu)**2 / (2 * sig**2))


def linear(x, m, b):
    return m * x + b
