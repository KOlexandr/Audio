__author__ = 'Olexandr'


class LibraryItem:
    def __init__(self, word, samples):
        self.word = word
        self.samples = samples
        self.length = len(samples)
        self.fft = None

    def correct_length(self, new_length):
        """
        change size of list (make it bigger) and add zeros to needle length
        @param new_length: new length of list
        @return: list has new length and 0 in the end
        """
        if self.length < new_length:
            self.samples = list(self.samples) + [0] * (new_length - self.length)
        elif self.length > new_length:
            raise Exception("New length must by bigger than current!")

    def count_fft(self, fft_function):
        """
        count FFT of samples of this item
        @param fft_function: function for counting FFT
        """
        if self.fft is None:
            self.fft = fft_function(self.samples)