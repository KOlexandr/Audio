import math

__author__ = 'Olexandr'


def zero_crossing_rate(data):
    zcr = 0
    for i in range(1, len(data)):
        if data[i]*data[i-1] < 0:
            zcr += 1
    return zcr


def energy_logarithm(vector):
    return math.log10((abs(sum(map(lambda x: x**2, vector)))+0.001)/(len(vector)))