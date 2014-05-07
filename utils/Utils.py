import os
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


def correct_len(x, new_length=None, is_pow_of_2=False):
    """
    change size of list (make it bigger) and add zeros to needle length
    @param x: list of numbers
    @param new_length: new length of list
    @param is_pow_of_2: flag mean than length must be power of 2
    @return: list with new length and 0 in the end
    """
    if not new_length:
        new_length = len(x)
    if len(x) > new_length:
        raise Exception("New length must by bigger than current!")
    if is_pow_of_2 and not is_power_of_2(new_length):
        new_length = 2**next_power_of_2(new_length)
    return list(x) + [0]*(new_length - len(x))


def get_files(base_folder, extension):
    """
    find all files in base_folder and all folders inside base
    @param base_folder: start directory
    @param extension: extension of file
    @return: list of paths to files
    """
    file_paths = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith(extension):
                file_paths.append(os.path.join(root, file))
    return file_paths


def get_simple_file_names(base_folder, extension):
    """
    find all files in base_folder and all folders inside base
    @param base_folder: start directory
    @param extension: extension of file
    @return: list of simple file names with given extension
    """
    file_list = []
    for root, dirs, files in os.walk(base_folder):
        for i in files:
            if str(i).lower().endswith(extension.lower()):
                file_list.append(i)
    return file_list