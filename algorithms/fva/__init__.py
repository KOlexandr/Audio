from algorithms.fir import FiniteImpulseFilter
from variables import path_to_examples, path_to_silence, path_to_test, use_filter
from handlers.Recorder import Recorder
from beans.Library import Library
from beans.WavFile import WavFile
from utils.Utils import get_files
import numpy as np

__author__ = 'Olexandr'


class FFTVoiceAnalyzer:
    def __init__(self, base_lib_folder, fft, silence, really_transform=False):
        """
        @param base_lib_folder: base folder with example files
        @param fft: function for counting FFT
        @param silence: "silence" example WavFile
        @param really_transform: is really transform few channels to one or use one channel without transformation
        self.extension: extension of audio files which will use
        """
        self.fft = fft
        self.silence = silence
        self.extension = ".wav"
        self.recorder = Recorder()
        self.base_lib_folder = base_lib_folder
        self.really_transform = really_transform
        if use_filter:
            self.filter_fft = lambda sam, fr=None: FiniteImpulseFilter.filter(abs(self.fft(sam)), 50, fr,
                                                                              win_func="hemming")
        else:
            self.filter_fft = lambda sam, fr=None: abs(self.fft(sam))

        self.lib = self.create_lib_with_examples()

    def create_lib_with_examples(self):
        """
        creates new library and adds all files from base folder as items
        @return: new Library object
        """
        example_waves = WavFile.get_all_waves(get_files(self.base_lib_folder, self.extension))
        lib = Library(self.fft, really_transform=self.really_transform)
        for i in example_waves:
            lib.create_and_add_item_from_wave(i)
        return lib

    def find_word_in_test_file(self, test):
        """
        analyze test file (finds all silence and split file to few pars by them)
        @param test: recorded audio
        @return: samples of each found word, word count, max length of word (array of samples)
        """
        start_idx = 0
        indexes, coefficients = [], []
        length_of_silence = len(self.silence.get_one_channel_data())
        silence_samples = self.filter_fft(self.silence.get_one_channel_data())
        for i in range(int(len(test.get_one_channel_data()) / length_of_silence)):
            f = test.get_one_channel_data()[start_idx:start_idx + length_of_silence]
            test_samples = self.filter_fft(f)
            tmp = np.corrcoef(silence_samples, test_samples)
            coefficients.append(abs(tmp[0][1]))
            indexes.append((start_idx, start_idx + length_of_silence))
            start_idx += length_of_silence
        j = 0
        k = 0
        max_length = words_count = 0
        words_samples = []
        while j < len(coefficients):
            start = j
            while j < len(coefficients) and coefficients[j] < 0.3:
                j += 1
                k += 1
            finish = j - 1
            if k > 0:
                words_count += 1
                tmp = test.get_one_channel_data()[indexes[start][0]:indexes[finish][1]]
                max_length = max(max_length, len(tmp))
                words_samples.append(tmp)
                k = 0
            j += 1
        return words_samples, words_count, max_length

    @staticmethod
    def analyze(wav, analyzer):
        samples, word_count, max_len = analyzer.find_word_in_test_file(wav)
        result = "All words in file = " + str(word_count) + "\n"
        for j in samples:
            word, coefficient = analyzer.lib.find_max_corrcoef_and_word(j, max_len)
            if coefficient > 0.3:
                result += word + " - " + str(coefficient) + "\n"
        return result


if "__main__" == __name__:
    processor = FFTVoiceAnalyzer(path_to_examples, np.fft.fft, WavFile(path_to_silence))
    print(FFTVoiceAnalyzer.analyze(WavFile(path_to_test + "12345.wav"), processor))