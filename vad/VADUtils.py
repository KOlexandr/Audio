from functools import reduce
import math

__author__ = 'Olexandr'


def zero_crossing_rate(data):
    zcr = 0
    for i in range(1, len(data)):
        if data[i]*data[i-1] < 0:
            zcr += 1
    return zcr


def energy_logarithm(data):
    """
    Short-term energy
    """
    return math.log10((abs(sum(map(lambda x: x**2, data)))+0.001)/len(data))


def sfm(data):
    """
    Spectral Flatness Measure
    """
    return 10*math.log10(gm(data)/am(data))


def gm(data):
    """
    Geometric mean
    """
    return reduce(lambda x, y: x * y, data, 1)**(1/len(data))


def am(data):
    """
    Arithmetic mean
    """
    return reduce(lambda x, y: x + y, data, 0)/len(data)