__author__ = 'Olexandr'


def find_value(value, data_class, eps):
    for i in range(len(data_class)):
        if abs(value - data_class[i][0]) < eps:
            return i, data_class[i][1]
    return -1, 0