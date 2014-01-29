import numpy as np
from WavFile import WavFile
from Recorder import Recorder
from library.Library import Library
from utils.FileSystemUtils import get_files
from utils.Utils import get_all_waves

__author__ = 'Olexandr'


def create_lib_with_examples(base_folder, fft_function):
    example_waves = get_all_waves(get_files(base_folder, ".wav"))
    lib = Library(fft_function)
    for i in example_waves:
        lib.create_and_add_item_from_wave(i)
    return lib


def get_silence():
    return WavFile("waves/silenceSmall.wav").get_one_channel_data()


def find_word_in_test_file(test_samples, silence, fft_function):
    start_idx = 0
    indexes = []
    coefficients = []
    #silence = Utils.correct_len(silence, 2 ** Utils.what_next_power_of_2(len(silence)))
    length_of_silence = len(silence)
    for i in range(int(len(test_samples) / length_of_silence)):
        f = test_samples[start_idx:start_idx + length_of_silence]
        tmp = np.corrcoef(abs(fft_function(silence)), abs(fft_function(f)))
        coefficients.append(abs(tmp[0][1]))
        indexes.append((start_idx, start_idx + length_of_silence))
        start_idx += int(length_of_silence)
    j = 0
    k = 0
    max_len = 0
    words_count = 0
    words_samples = []
    while j < len(coefficients):
        start = j
        while j < len(coefficients) and coefficients[j] < 0.3:
            j += 1
            k += 1
        finish = j - 1
        if k > 0:
            words_count += 1
            tmp = test_samples[indexes[start][0]:indexes[finish][1]]
            max_len = max(max_len, len(tmp))
            words_samples.append(tmp)
            k = 0
        j += 1
    return words_samples, coefficients, words_count, max_len


def main():
    recorder = Recorder()
    lib = create_lib_with_examples("examples", np.fft.fft)
    samples, coefficients, word_count, max_len = find_word_in_test_file(
        recorder.record_and_get_wav(5).get_one_channel_data(),
        get_silence(), lib.fft_function)
    print("All words in file = " + str(word_count))
    for j in samples:
        word, coefficient = lib.find_max_corrcoef_and_word(j, max_len)
        print(word + " - " + str(coefficient))


# main()

# w = WavFile("waves/12345678910.wav")
# print(w.get_one_channel_data())