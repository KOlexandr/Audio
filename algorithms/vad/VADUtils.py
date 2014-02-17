import numpy
from math import log10
from scipy import stats

__author__ = 'Olexandr'


def zero_crossing_rate(data):
    """
    Zero Crossing Rate
    """
    zcr = 0
    for i in range(1, len(data)):
        if numpy.float64(data[i]) * numpy.float64(data[i - 1]) < 0:
            zcr += 1
    return zcr


def energy_logarithm(data):
    """
    Short-term energy
    """
    return log10((abs(sum(map(lambda x: numpy.float64(x) * numpy.float64(x), data))) + 0.001) / len(data))


def sfm(data):
    """
    Spectral Flatness Measure
    """
    g = stats.gmean(data, dtype=numpy.float64) + 0.00001
    a = numpy.mean(data, dtype=numpy.float64)
    return 10 * log10(g / a)


def find_start(data, boundary):
    """
    find indexes of starts of words in data
    @param data: array
    @param boundary: boundary value of parameter
    @return: array with start indexes
    """
    idx, starts = [], []
    for i in range(1, len(data)):
        if data[i] >= boundary > data[i - 1]:
            idx.append(i)
    for i in range(len(idx)):
        if idx[i] != 0:
            starts.append(idx[i])
    return starts


def find_end(data, boundary, start):
    """
    find nearest end index of word for given start index
    @param data: array
    @param boundary: boundary value of parameter
    @param start: word start index
    @return: word end index
    """
    idx = 0
    for i in range(start, len(data)):
        if data[i] < boundary:
            return i
    if idx == 0:
        idx = len(data) - 1
    return idx


def find_words(starts, ends, min_frames_voice, min_frames_noise):
    """
    find indexes of start and and word in list which represent audio file
    @param starts: start indexes of possible words
    @param ends: end indexes of possible words
    @param min_frames_voice: minimum number of consecutive frames to be classified as a "language"
                    to distinguish them as "word"
    @param min_frames_noise: minimum number of consecutive frames to be classified as "noise"
                    to skip and do not take into account their
    @return: 2 lists with start indexes and end indexes of words
    """
    word_lengths, noise_lengths, word_starts, word_ends = [], [], [], []
    for i in range(len(starts)-1):
        word_lengths.append(ends[i] - starts[i])
        noise_lengths.append(starts[i+1] - ends[i])
    word_lengths.append(ends[len(starts)-1] - starts[len(starts)-1])

    i, j = 0, 0
    while i < len(starts):
        if word_lengths[i] > min_frames_voice:
            word_starts.append(starts[i])
            word_ends.append(0)
            t = 0
            for k in range(i, len(starts)-1):
                if noise_lengths[k] > min_frames_noise:
                    word_ends[len(word_ends)-1] = ends[k]
                    i = t = k
                    break
            if t != i or word_ends[j] == 0:
                word_ends[j] = ends[len(starts)-1]
            j += 1
        i += 1
    for i in range(len(word_starts)-1):
        if word_starts[i+1] < word_ends[i]:
            word_ends[i] = word_starts[i+1]-1
    return word_starts, word_ends


def find_words_for_one_param(param, low_value, min_frames_voice, min_frames_noise):
    """
    find indexes of starts and ends of words using given characteristic
                (Short-time Energy, Most Dominant Frequency Component, Zero Crossing Rate, Spectral Flatness Measure)
    @param param: characteristic list
    @param low_value: boundary value of noise
    @param min_frames_voice: minimum number of consecutive frames to be classified as a "language"
                    to distinguish them as "word"
    @param min_frames_noise: minimum number of consecutive frames to be classified as "noise"
                    to skip and do not take into account their
    @return: 2 lists with start indexes and end indexes of words
    """
    starts = find_start(param, low_value)
    ends = []
    for i in range(len(starts)):
        ends.append(find_end(param, low_value, starts[i]))
    [word_starts, word_ends] = find_words(starts, ends, min_frames_voice, min_frames_noise)
    return word_starts, word_ends
