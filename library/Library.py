import numpy as np
from utils.LengthUtils import correct_len
from library.LibraryItem import LibraryItem
from utils.PowerUtils import is_power_of_2, next_power_of_2

__author__ = 'Olexandr'


class Library:
    def __init__(self, fft_function, is_pow_of_2=False):
        """
        initialize new library
        @param fft_function: function for count FFT of array
        @param is_pow_of_2: flag that means that length of array for FFT must be power of 2
        """
        #library items(words)
        self.items = []
        #counter of items
        self.item_count = 0
        #max length of one item (length of array of samples)
        self.max_length = 0
        self.fft_function = fft_function
        self.length_is_power_of_2 = is_pow_of_2

    def create_and_add_item(self, word, samples):
        """
        creates new library item with using string (word) and samples array
        @param word: word
        @param samples: array of numbers
        """
        item = LibraryItem(word, samples)
        self.items.append(item)
        self.item_count += 1
        self.max_length = max(self.max_length, len(samples))

    def add_item(self, item):
        """
        adds one item to library
        @param item:
        """
        self.items.append(item)
        self.item_count += 1
        self.max_length = max(self.max_length, len(item.samples))

    def create_and_add_item_from_wave(self, wave_file):
        """
        creates new library item with using WavFile object
        @param wave_file:
        """
        item = LibraryItem(wave_file.get_simple_file_name(), wave_file.get_one_channel_data())
        self.items.append(item)
        self.item_count += 1
        self.max_length = max(self.max_length, len(item.samples))

    def correct_length_of_all_items(self):
        """
        correct length of all items in library
        """
        if not is_power_of_2(self.max_length) and self.length_is_power_of_2:
            self.max_length = 2 ** next_power_of_2(self.max_length)
        for i in self.items:
            i.correct_length(self.max_length)

    def count_fft_for_all_items(self):
        """
        count FFT of all items in library
        """
        for i in self.items:
            i.count_fft(self.fft_function)

    def find_max_corrcoef_and_word(self, test_samples, max_len):
        self.max_length = max(self.max_length, max_len)
        self.correct_length_of_all_items()
        self.count_fft_for_all_items()
        word, coefficient = None, 0
        test_fft = self.fft_function(correct_len(test_samples, self.max_length))
        for i in self.items:
            tmp_coefficient = np.corrcoef(abs(i.fft), abs(test_fft))
            if tmp_coefficient[0][1] > coefficient:
                word = i.word
                coefficient = tmp_coefficient[0][1]
        return word, coefficient