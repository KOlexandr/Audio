from utils.Utils import correct_len, is_power_of_2
import numpy as np

__author__ = 'Olexandr'


def fft(x):
    """A recursive implementation of the 1D Cooley-Tukey FFT"""
    x = np.asarray(x, dtype=float)
    n = x.shape[0]

    if n % 2 > 0:
        raise ValueError("size of x must be a power of 2")
    elif n <= 32:  # this cutoff should be optimized
        return dft_slow(x)
    else:
        x_even = fft(x[::2])
        x_odd = fft(x[1::2])
        factor = np.exp(-2j * np.pi * np.arange(n) / n)
        return np.concatenate([x_even + factor[:n / 2] * x_odd,
                               x_even + factor[n / 2:] * x_odd])


def dft_slow(x):
    """Compute the discrete Fourier Transform of the 1D array x"""
    x = np.asarray(x, dtype=float)
    array = x.shape[0]
    n = np.arange(array)
    k = n.reshape((array, 1))
    m = np.exp(-2j * np.pi * k * n / array)
    return np.dot(m, x)


def fft_diff_len(x):
    """
    Fast Fourier transform for different lists which can have length not power of 2
    function correct length and if all ok run fft
    @param x: list of data
    @return: list with fft
    """
    if is_power_of_2(len(x)):
        return fft(x)
    else:
        return fft_diff_len(correct_len(x, is_pow_of_2=True))