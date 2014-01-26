__author__ = 'Olexandr'

import os
import FFT
import numpy as np
from WavFile import WavFile


def get_files(base_folder):
    """
    find all files in base_folder and all folders inside base
    @param base_folder: start directory
    @return: list of paths to files
    """
    file_paths = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith(".wav"):
                file_paths.append(os.path.join(root, file))
    return file_paths


def get_all_waves(files_list):
    """
    get all files from list and create list of WavFile objects
    @param files_list: list of paths to files
    @return: list of WavFile objects
    """
    waves = []
    for i in files_list:
        waves.append(WavFile(i))
    return waves


def get_dict_with_samples(waves):
    """
    make dict of file names as key and samples (with corrected length) of wav file as value
    @param waves: list of WavFile
    @return: dict, maximum length of file sample
    """
    max_len = 0
    waves_name = []
    waves_channel = []
    for i in waves:
        data = i.get_one_channel_data()
        waves_channel.append(data)
        waves_name.append(i.get_simple_file_name())
        max_len = max(max_len, len(data))

    waves_corrected_len = []
    for i in waves_channel:
        waves_corrected_len.append(correct_len(i, new_length=max_len, is_pow_of_2=True))
    return dict(zip(waves_name, waves_corrected_len)), 2**what_next_power_of_2(max_len)


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
        new_length = 2**what_next_power_of_2(new_length)
    return list(x) + [0]*(new_length - len(x))


def is_power_of_2(value):
    """
    verify is number is power of 2
    @param value: value for verification
    @return: True or False
    """
    if value % 2 != 0:
        return False
    while value % 2 == 0:
        value /= 2
    return value == 1


def what_next_power_of_2(number):
    """
    find next power of 2/ for this power number must be >= than input
    @param number: value for verification
    @return: power of 2
    """
    power = 0
    count = 0
    while number > 1:
        if number % 2 == 1:
            count += 1
        number = int(number / 2)
        power += 1
    if count == 0:
        return power
    else:
        return power + 1


def get_dict_with_fft(dict_waves):
    """
    find fft of samples
    @param dict_waves: dict with file names and samples
    @return: new dict with file names as keys and fft value of samples as values
    """
    file_names = dict_waves.keys()
    fft_dict = {}
    for i in file_names:
        fft_dict[i] = abs(FFT.fft_diff_len(dict_waves.get(i)))
    return fft_dict


def process_one_wav(wav_file, length):
    """
    process one wav file and return fft of its sample
    @param wav_file: WavFile object
    @param length: length of examples sample
    @return: list with fft of sample
    """
    data = wav_file.get_one_channel_data()
    data = correct_len(data, new_length=length, is_pow_of_2=True)
    return abs(FFT.fft_diff_len(data))


def process_examples(base_folder):
    """
    process all example files from base folder and all inside folder
    @param base_folder:
    @return: dict with file names as keys and fft as values
    """
    dict_with_samples, length = get_dict_with_samples(get_all_waves(get_files(base_folder)))
    return get_dict_with_fft(dict_with_samples), length


def corrcoef(dict_of_examples, test_file):
    """
    find coefficient of correlation between all examples and test file
    and find maximum value of it for test file, return name of file and coefficient of correlation
    @param dict_of_examples: dict with name of file as keys and fft as values
    @param test_file: fft of test file
    @return: name of file with max corrcoef and corrcoef
    """
    file_names = list(dict_of_examples.keys())
    fft = []
    for i in file_names:
        fft.append(list(dict_of_examples.get(i)))

    fft.append(list(test_file))
    coefficients = np.corrcoef(fft)
    needle = list(coefficients[len(coefficients)-1])
    word = file_names[0]
    max_coefficient = needle[0]
    for i in range(len(file_names)):
        if max_coefficient < needle[i]:
            max_coefficient = needle[i]
            word = file_names[i]
    return word, max_coefficient