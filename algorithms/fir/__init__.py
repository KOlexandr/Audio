from handlers.Plotter import Plotter
from variables import path_to_test
from beans.WavFile import WavFile
from algorithms.fft import FFT
import ctypes
import os

__author__ = 'Olexandr'

path_to_dll = os.path.dirname(__file__) + "/FIR.dll"


class FiniteImpulseFilter:
    """
    Filter with finite impulse response
    """
    window_function = {
        "square": 0,
        "hann": 1,
        "hemming": 2,
        "blackman": 3
    }

    @staticmethod
    def filter(in_data, filter_length, frame_rate, fb=20, fba=50, win_func="square"):
        """
        @param in_data: vector of input data (vector after fft transform)
        @param filter_length: length of filter (biggest length - slower program)
        @param frame_rate: sampling frequency input
        @param fb: The frequency bandwidth
        @param fba: Frequency band attenuation
        @param win_func: name of window function
        @return: filtered vector of fft data
        """
        dll = ctypes.CDLL(path_to_dll)
        size = len(in_data)
        in_data_c = (ctypes.c_double * size)()
        out_data_c = (ctypes.c_double * size)()
        in_data_c[:] = in_data[:]
        code = int(FiniteImpulseFilter.window_function[win_func])
        dll.filter(in_data_c, out_data_c, ctypes.c_int(size), ctypes.c_int(filter_length),
                   ctypes.c_int(frame_rate), ctypes.c_int(fb), ctypes.c_int(fba), ctypes.c_int(code))
        return list(out_data_c)


def test():
    file = WavFile(path_to_test + "12345678910.wav")
    freq, amplitude = FFT.fft_db_amplitude_wav(file)
    out = FiniteImpulseFilter.filter(amplitude, 100, file.frame_rate, 20, 50, "hemming")

    file_plotter = Plotter("FIR Test DAF")
    file_plotter.add_sub_plot_data("Digitized audio file", file.samples, x_label="Samples", y_label="Amplitude")
    file_plotter.sub_plot_all_horizontal()

    fft_plotter = Plotter("FIR Test FFT")
    fft_plotter.add_sub_plot_data("Fast Fourier Transform", amplitude, freq, scale_x='log', scale_y='log',
                                  x_label="Frequency (Hz)", y_label="Amplitude (db)")
    fft_plotter.sub_plot_all_horizontal()

    fft_plotter = Plotter("FIR Test FIR_FFT")
    fft_plotter.add_sub_plot_data("Fast Fourier Transform After FIR", out, freq, scale_x='log', scale_y='log',
                                  x_label="Frequency (Hz)", y_label="Amplitude (db)")
    fft_plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    test()