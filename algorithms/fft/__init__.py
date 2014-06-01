from utils.Utils import correct_len, is_power_of_2
from handlers.Plotter import Plotter
from variables import path_to_test
from beans.WavFile import WavFile
import numpy as np
import ctypes
import numpy
import math
import os

__author__ = 'Olexandr'


path_to_dll = os.path.dirname(__file__) + "/FFT.dll"


class FFT:
    """
    http://habrahabr.ru/post/219337
    Fast Fourier Transform
    """

    @staticmethod
    def fft(wav):
        """
        wrapper for c++ fft from FFT.dll
        @param wav: custom WavFile
        @return: freq - vector of frequency (Hz), amplitude - vector of amplitudes (db)
        """
        dll = ctypes.CDLL(path_to_dll)
        p2 = int(math.log2(wav.samples.nbytes/wav.sample_width))
        array_size = 1 << p2
        in_data = (ctypes.c_double * (array_size * 2))()
        out_data = (ctypes.c_double * (array_size * 2))()

        min_size = min(array_size * 2, len(wav.samples))
        in_data[0:min_size] = wav.samples[0:min_size]

        dll.fft(ctypes.c_int(p2), in_data, out_data)
        out = [0]*(array_size * 2)
        for i in range(array_size * 2):
            out[i] = out_data[i]

        #magnitude of spectrum
        amplitude = []
        freq = []
        current_freq = 0
        delta = float(wav.frame_rate)/float(array_size)
        for i in range(0, array_size, 2):
            amplitude.append(math.sqrt(out[i]*out[i]+out[i+1]*out[i+1]))
            freq.append(current_freq)
            current_freq += delta
        return freq, amplitude

    @staticmethod
    def fft_db_amplitude_wav(wav):
        """
        wrapper for c++ fft_db_hz from FFT.dll
        create freq and amplitude vectors in c++-code (works more faster then FFT.fft)
        @param wav: custom WavFile
        @return: freq - vector of frequency (Hz), amplitude - vector of amplitudes (db)
        """
        return FFT.fft_db_amplitude(wav.samples, wav.samples.nbytes, wav.sample_width, wav.frame_rate)

    @staticmethod
    def fft_db_amplitude(samples, byte_per_frame, sample_width, frame_rate):
        """
        wrapper for c++ fft_db_hz from FFT.dll
        create freq and amplitude vectors in c++-code (works more faster then FFT.fft)
        @param samples: vector of audio data
        @param byte_per_frame: values for representation each frame (2)
        @param sample_width: width of each sample
        @param frame_rate: frame rate of samples (44100 Hz)
        @return: freq - vector of frequency (Hz), amplitude - vector of amplitudes (db)
        """
        dll = ctypes.CDLL(path_to_dll)
        p2 = int(math.log2(byte_per_frame/sample_width))
        array_size = 1 << p2
        in_data = (ctypes.c_double * (array_size*2))()
        freq = (ctypes.c_double * array_size)()
        amplitude = (ctypes.c_double * array_size)()

        min_size = min(array_size * 2, len(samples))
        in_data[0:min_size] = samples[0:min_size]

        dll.fft_db_hz(ctypes.c_int(p2), ctypes.c_int(frame_rate), in_data, freq, amplitude)

        return list(freq), list(amplitude)

    @staticmethod
    def create_sin_test(time, sample_rate, file_name=None, amplitude=32767, freq_hz=100, is_plot=False):
        """
        create test audio file with sin
        @param time: length of audio (seconds)
        @param sample_rate: sample rate (44100 Hz for example)
        @param file_name: name of file for save or None, if you don't wont to save file
        @param amplitude: max amplitude
        @param freq_hz: dominant frequency
        @param is_plot: flag for plot file data
        """
        buf_size = sample_rate*time

        buffer = list(numpy.zeros(buf_size, int))
        for i in range(buf_size):
            buffer[i] += int(amplitude * math.sin(float(2 * math.pi * i * freq_hz / sample_rate)))

        if is_plot:
            plotter = Plotter()
            plotter.add_sub_plot_data("data", buffer)
            plotter.sub_plot_all_horizontal()

        if not file_name is None:
            WavFile.write(file_name, buffer, time)

    @staticmethod
    def fft_p(x):
        """A recursive implementation of the 1D Cooley-Tukey FFT"""
        x = np.asarray(x, dtype=float)
        n = x.shape[0]

        if n % 2 > 0:
            raise ValueError("size of x must be a power of 2")
        elif n <= 32:  # this cutoff should be optimized
            return FFT.dft_slow(x)
        else:
            x_even = FFT.fft(x[::2])
            x_odd = FFT.fft(x[1::2])
            factor = np.exp(-2j * np.pi * np.arange(n) / n)
            return np.concatenate([x_even + factor[:n / 2] * x_odd,
                                   x_even + factor[n / 2:] * x_odd])

    @staticmethod
    def dft_slow(x):
        """Compute the discrete Fourier Transform of the 1D array x"""
        x = np.asarray(x, dtype=float)
        array = x.shape[0]
        n = np.arange(array)
        k = n.reshape((array, 1))
        m = np.exp(-2j * np.pi * k * n / array)
        return np.dot(m, x)

    @staticmethod
    def fft_diff_len(x):
        """
        Fast Fourier transform for different lists which can have length not power of 2
        function correct length and if all ok run fft
        @param x: list of data
        @return: list with fft
        """
        if is_power_of_2(len(x)):
            return FFT.fft(x)
        else:
            return FFT.fft_diff_len(correct_len(x, is_pow_of_2=True))


def test():
    wav = WavFile(path_to_test + '12345678910.wav')
    freq, amplitude = FFT.fft(wav)
    freq1, amplitude1 = FFT.fft_db_amplitude_wav(wav)

    plotter = Plotter()
    plotter.add_sub_plot_data("data", wav.samples)
    plotter.add_sub_plot_data("fft_log_fft", amplitude, freq, scale_x='log', scale_y='log')
    plotter.add_sub_plot_data("fft_log_fft_db_hz", amplitude1, freq1, scale_x='log', scale_y='log')

    plotter.sub_plot_all_horizontal()


def test_all_audio():
    sin = WavFile(path_to_test + 'sin100Hz.wav')
    noise = WavFile(path_to_test + 'noise.wav')
    m = WavFile(path_to_test + 'meandr25Hz.wav')
    freq_sin, amplitude_sin = FFT.fft_db_amplitude_wav(sin)
    freq_noise, amplitude_noise = FFT.fft_db_amplitude_wav(noise)
    freq_m, amplitude_m = FFT.fft_db_amplitude_wav(m)

    plotter = Plotter()
    plotter.add_sub_plot_data("sin 100 Hz", sin.samples)
    plotter.add_sub_plot_data("fft sin 100 Hz", amplitude_sin, freq_sin, scale_x='log', scale_y='log')
    plotter.add_sub_plot_data("noise", noise.samples)
    plotter.add_sub_plot_data("fft noise", amplitude_noise, freq_noise, scale_y='log')
    plotter.add_sub_plot_data("meandr25Hz", m.samples)
    plotter.add_sub_plot_data("fft meandr 25 Hz", amplitude_m[0:2500], freq_m[0:2500], scale_y='log')

    plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    test()
    # test_all_audio()