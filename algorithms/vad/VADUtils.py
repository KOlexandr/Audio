import numpy
from math import log10
from scipy import stats

__author__ = 'Olexandr'


def zero_crossing_rate(data):
    zcr = 0
    for i in range(1, len(data)):
        if numpy.float64(data[i]) * numpy.float64(data[i - 1]) < 0:
            zcr += 1
    return zcr


def energy_logarithm(data):
    """
    Short-term energy
    """
    return log10((abs(sum(map(lambda x: numpy.float64(x)*numpy.float64(x), data))) + 0.001) / len(data))


def sfm(data):
    """
    Spectral Flatness Measure
    """
    g = stats.gmean(data, dtype=numpy.float64) + 0.00001
    a = numpy.mean(data, dtype=numpy.float64)
    return 10 * log10(g/a)