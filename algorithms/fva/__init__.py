from variables import path_to_examples, path_to_silence, path_to_waves
from handlers.Recorder import Recorder
from beans.Library import Library
from beans.WavFile import WavFile
from utils.Utils import get_files
import numpy as np

__author__ = 'Olexandr'


class FFTVoiceAnalyzer:

    def __init__(self, base_lib_folder, fft, get_silence, really_transform=False):
        """
        @param base_lib_folder: base folder with example files
        @param fft: function for counting FFT
        @param get_silence: function for get "silence" example file
        @param really_transform: is really transform few channels to one or use one channel without transformation
        self.extension: extension of audio files which will use
        """
        self.fft = fft
        self.recorder = Recorder()
        self.extension = ".wav"
        self.get_silence = get_silence
        self.base_lib_folder = base_lib_folder
        self.really_transform = really_transform

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

    def find_word_in_test_file(self, test_samples):
        """
        analyze test file (finds all silence and split file to few pars by them)
        @param test_samples: samples of recorded audio
        @return: samples of each found word, word count, max length of word (array of samples)
        """
        start_idx = 0
        indexes, coefficients = [], []
        silence = self.get_silence()
        length_of_silence = len(silence)
        for i in range(int(len(test_samples) / length_of_silence)):
            f = test_samples[start_idx:start_idx + length_of_silence]
            tmp = np.corrcoef(abs(self.fft(silence)), abs(self.fft(f)))
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
                tmp = test_samples[indexes[start][0]:indexes[finish][1]]
                max_length = max(max_length, len(tmp))
                words_samples.append(tmp)
                k = 0
            j += 1
        return words_samples, words_count, max_length

    @staticmethod
    def analyze(wav, analyzer):
        samples, word_count, max_len = analyzer.find_word_in_test_file(wav.get_one_channel_data())
        result = "All words in file = " + str(word_count) + "\n"
        for j in samples:
            word, coefficient = analyzer.lib.find_max_corrcoef_and_word(j, max_len)
            if coefficient > 0.3:
                result += word + " - " + str(coefficient) + "\n"
        return result


if "__main__" == __name__:
    processor = FFTVoiceAnalyzer(path_to_examples, np.fft.fft, lambda: WavFile(path_to_silence).get_one_channel_data())
    FFTVoiceAnalyzer.analyze(WavFile(path_to_waves + "13245678109Speed.wav"), processor)