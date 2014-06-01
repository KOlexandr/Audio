import struct
import wave
import scipy
from variables import path_to_test, path_to_vad_results
from handlers.Plotter import Plotter
from beans.WavFile import WavFile
from math import log10, floor
from scipy import stats
import numpy

__author__ = 'Olexandr'


def vad(wav_file, frame_size=10, fft_function=numpy.fft.fft):
    """
    Voice Activity Detection (http://habrahabr.ru/post/192954)
    @param wav_file: WavFile object
    @param frame_size: size of one frame in milliseconds
    @param fft_function: function for count FFT
    @return: tuple of next parameters
            energy          - Short-term energy for each frame,                      (MatLab)
            freq_component  - Most Dominant Frequency Component for each frame,      (MatLab)
            zcr             - Zero Crossing Rate for each frame,                     (MatLab)
            sfm_list        - Spectral Flatness Measure for each frame,              (new)
            items_per_frame - items in one frame,                                    (MatLab)
            speech          - list with flags for each frame (silence or speech)     (new)
    """
    data = wav_file.get_one_channel_data()
    frame_count = int(wav_file.get_file_size_msec() / frame_size)
    items_per_frame = floor(len(data) / frame_count)

    #Threshold for Energy
    energy_prim_threshold = 40
    #Threshold for Most Dominant Frequency Component (Hz)
    freq_prim_threshold = 185
    #Threshold for Spectral Flatness Measure
    sfm_prim_threshold = 5
    #Threshold for Zero Crossing Rate
    zcr_prim_threshold = 20

    silence_count = 0
    thresh_energy, thresh_zcr, thresh_freq, thresh_sfm = 0, 0, 0, 0
    energy, zcr, freq_component, sfm_list, speech = [], [], [], [], []

    j = 0
    for i in range(frame_count):
        sub = data[i * items_per_frame:(i + 1) * items_per_frame]

        energy.append(energy_logarithm(sub))
        zcr.append(zero_crossing_rate(sub))
        freq_component.append(max(sub))

        sfm_list.append(sfm(abs(fft_function(sub))))

        min_energy = min(energy)
        min_zcr = min(zcr)
        min_freq = min(freq_component)
        min_sfm = min(sfm_list)

        if min_energy < 0:
            min_energy = 0.001

        if j < 5:
            thresh_energy = energy_prim_threshold * log10(min_energy)
            thresh_zcr = zcr_prim_threshold
            thresh_freq = freq_prim_threshold
            thresh_sfm = sfm_prim_threshold

        counter = 0
        if (energy[i] - min_energy) >= thresh_energy:
            counter += 1
        if (zcr[i] - min_zcr) >= thresh_zcr:
            counter += 1
        # if (freq_component[i] - min_freq) >= thresh_freq:
        #     counter += 1
        if (sfm_list[i] - min_sfm) >= thresh_sfm:
            counter += 1

        if counter > 1:
            speech.append(1)
        else:
            speech.append(0)
            silence_count += 1

        if speech[i] == 0:
            min_energy = (silence_count * min_energy + energy[i]) / (silence_count + 1)
        thresh_energy = energy_prim_threshold * log10(abs(min_energy)+1e-5)

    return {"energy": energy,
            "mdf": freq_component,
            "zcr": zcr,
            "sfm": sfm_list,
            "items_per_frame": items_per_frame,
            "speech": speech,
            "words_count": len(energy)}


def simple_vad(wav_file, frame_size=10, fft_function=numpy.fft.fft):
    """
    simple Voice Activity Detection (without some verifications etc.)
    @param wav_file: WavFile object
    @param frame_size: size of one frame in milliseconds
    @param fft_function: function for count FFT
    @return: tuple of next parameters
            energy          - Short-term energy for each frame,                      (MatLab)
            mdf  - Most Dominant Frequency Component for each frame,                 (MatLab)
            zcr             - Zero Crossing Rate for each frame,                     (MatLab)
            sfm_list        - Spectral Flatness Measure for each frame,              (new)
            items_per_frame - items in one frame,                                    (MatLab)
    """
    data = wav_file.get_one_channel_data()
    frame_count = int(wav_file.get_file_size_msec() / frame_size)
    items_per_frame = floor(len(data) / frame_count)
    energy, zcr, mdf, sfm_list, speech = [], [], [], [], []
    for i in range(frame_count):
        sub = data[i * items_per_frame:(i + 1) * items_per_frame]
        energy.append(energy_logarithm(sub))
        zcr.append(zero_crossing_rate(sub))
        mdf.append(max(sub))
        sfm_list.append(sfm(abs(fft_function(sub))))
    return {"energy": energy,
            "mdf": mdf,
            "zcr": zcr,
            "sfm": sfm_list,
            "items_per_frame": items_per_frame,
            "words_count": len(energy)}


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


def plot_result(wav, word_results, params, min_params, colors, items):
    plot = Plotter()
    plot.add_sub_plot_data("samples", wav.get_one_channel_data())
    for i in word_results.keys():
        plot.add_line_at("samples", list(map(lambda x: x * items, word_results[i]["starts"])), "x", colors[i], lw=3)
        plot.add_line_at("samples", list(map(lambda x: x * items, word_results[i]["ends"])), "x", colors[i], lw=3)

    for i in word_results.keys():
        plot.add_sub_plot_data(i, params[i])
        plot.add_line_at(i, min_params[i], "y", color="red")
    plot.sub_plot_all_horizontal()


def create_files(wav, word_results, items):
    # channel1 = wav.samples[0::wav.number_of_channels]
    # channel2 = wav.samples[1::wav.number_of_channels]
    data = wav.get_one_channel_data()
    for i in word_results.keys():
        starts = word_results[i]['starts']
        ends = word_results[i]['ends']
        num = 1
        for k in range(0, len(starts)):
            WavFile.write(path_to_vad_results + 'word' + str(num) + "_" + str(i) + '.wav', data[starts[k]*items:ends[k]*items], 0)
            num += 1


def test(wav, min_frames_voice, min_frames_noise, bad_frames_count):
    keys, shifts = ["energy", "mdf", "zcr", "sfm"], {"energy": 1, "mdf": 320, "zcr": 1, "sfm": 1}
    colors = {"energy": "red", "mdf": "green", "zcr": "black", "sfm": "yellow"}
    params = vad(wav)
    min_params = {}
    if bad_frames_count == 0:
        for i in keys:
            min_params[i] = min(params[i]) + shifts[i]
    else:
        for i in keys:
            min_params[i] = max(params[i][0:bad_frames_count])
    word_results = {}
    for i in keys:
        if word_results.get(i) is None:
            word_results[i] = {}
        starts, ends = find_words_for_one_param(params[i], min_params[i], min_frames_voice, min_frames_noise)
        word_results[i]["starts"], word_results[i]["ends"] = starts, ends

    create_files(wav, word_results, params["items_per_frame"])
    plot_result(wav, word_results, params, min_params, colors, params["items_per_frame"])


if "__main__" == __name__:
    test(WavFile(path_to_test + "12345678910.wav"), 3, 3, 0)