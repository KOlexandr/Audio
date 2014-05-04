from algorithms.harmonicOscillations import HarmonicOscillations
from variables import path_to_project
from handlers.Plotter import Plotter
from beans.WavFile import WavFile
import ctypes
import os

__author__ = 'Olexandr'

path_to_dll = os.path.dirname(__file__) + "/FIR.dll"
path_to_audio = path_to_project + "/resources/audio_files/test/"


class FiniteImpulseFilter:
    """
    Filter with finite impulse response
    http://habrahabr.ru/post/128140
    """
    window_function = {
        "square": 0,
        "hann": 1,
        "hemming": 2,
        "blackman": 3
    }

    @staticmethod
    def filter(in_data, filter_length, frame_rate, fb, fba, win_func="square"):
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
    file = WavFile(path_to_audio + "meandr25Hz.wav")
    freq, amplitude = HarmonicOscillations.fft_db_amplitude_wav(file)
    out = FiniteImpulseFilter.filter(amplitude, 100, file.frame_rate, 20, 50, "hemming")

    plotter = Plotter()
    plotter.add_sub_plot_data("original", file.samples)
    plotter.add_sub_plot_data("fft", amplitude, freq, scale_x='log', scale_y='log')
    plotter.add_sub_plot_data("fft_filtered", out, freq, scale_x='log', scale_y='log')
    plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    test()