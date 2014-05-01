import math
import numpy as np

__author__ = 'Olexandr'


class Filter:
    """
    @param fs - The frequency bandwidth
    @param fx - Frequency band attenuation
    """

    def __init__(self, fs=20, fx=50, window_name="blackman", fft=np.fft.fft, really_transform=False, use_abs=True):
        windows = {
            "square": self.square_window_func,
            "hann": self.hann_window_func,
            "hemming": self.hemming_window_func,
            "blackman": self.blackman_window_func
        }
        self.fs = fs
        self.fx = fx
        self.fft = fft
        self.use_abs = use_abs
        self.really_transform = really_transform
        self.window_func = windows[window_name]

    def finite_impulse_filter(self, n, wav=None, in_data=None, fd=None):
        """
        @param wav - WavFile
        @param n - length of filter
        fd - Sampling frequency input
        """
        if not (wav is None):
            fd = wav.frame_rate
            in_data = wav.get_fft_of_wav(really_transform=self.really_transform, fft_func=self.fft, use_abs=self.use_abs)
        elif in_data is None or fd is None:
            raise Exception("Incorrect input data")
        out_data = [0] * len(in_data)

        #impulse characteristic of filter
        h = [0] * n
        #ideal impulse characteristic
        h_id = [0] * n
        #weight function
        w = [0] * n

        fc = (self.fs + self.fx) / (2 * fd)
        for i in range(n):
            if i == 0:
                h_id[i] = 2 * math.pi * fc
            else:
                h_id[i] = math.sin(2 * math.pi * fc * i) / (math.pi * i)
            w[i] = self.window_func(i, n)
            h[i] = h_id[i] * w[i]

        #Normalization of the impulse characteristic
        sum_of_coefficients = sum(h)
        h = list(map(lambda x: x / sum_of_coefficients, h))

        #Filtering input data
        for i in range(len(in_data)):
            out_data[i] = 0.0
            for j in range(n - 1):
                out_data[i] += h[j] * in_data[i - j]
        return out_data

    @staticmethod
    def square_window_func(i, n):
        """
        weight function for square window
        max side lobe level -13 db
        """
        if i <= 0 and i < n:
            return 1
        else:
            return 0

    @staticmethod
    def hann_window_func(i, n):
        """
        weight function for window of Hann
        side lobe level -31.5 db
        """
        return 0.5 * (1 - math.cos((2 * math.pi * i) / (n - 1)))

    @staticmethod
    def hemming_window_func(i, n):
        """
        weight function for window of Hemming
        side lobe level -42 db
        """
        return 0.53836 - 0.46164 * math.cos((2 * math.pi * i) / (n - 1))

    @staticmethod
    def blackman_window_func(i, n, alpha=0.16):
        """
        weight function for window of Blackman
        side lobe level -58 db (alpha=0.16)
        """
        a0 = (1 - alpha) / 2
        a1 = 0.5
        a2 = alpha / 2
        return a0 - a1 * math.cos((2 * math.pi * i) / (n - 1)) + a2 * math.cos((4 * math.pi * i) / (n - 1))