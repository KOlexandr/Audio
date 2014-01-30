import numpy as np
from WavFile import WavFile
from Recorder import Recorder
from library.Library import Library
from utils.FileSystemUtils import get_files

__author__ = 'Olexandr'


class Processor:

    def __init__(self, base_lib_folder, fft, get_silence, really_transform=False, extension=".wav"):
        """
        @param base_lib_folder: base folder with example files
        @param fft: function for counting FFT
        @param get_silence: function for get "silence" example file
        @param really_transform: is really transform few channels to one or use one channel without transformation
        @param extension: extension of audio files which will use
        """
        self.fft = fft
        self.recorder = Recorder()
        self.extension = extension
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