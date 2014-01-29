from math import log

__author__ = 'Olexandr'


def is_power_of(value, base):
    """
    verify is number is power of base
    @param value: value for verification
    @param base: base number
    @return: True or False
    """
    return log(value, base) == int(log(value, base))


def next_power_of(value, base):
    """
    find next power of base, for this power number must be >= than input
    @param value: value for verification
    @param base: base number
    @return: next power of base number
    """
    log_value = log(value, base)
    if log_value == int(log_value):
        return log_value
    else:
        return int(log_value) + 1


def next_power_of_2(value):
    return next_power_of(value, 2)


def is_power_of_2(value):
    return is_power_of(value, 2)
