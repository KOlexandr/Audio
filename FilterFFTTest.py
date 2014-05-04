from math import cos, pi
import numpy
from handlers.Plotter import Plotter
from beans.WavFile import WavFile

__author__ = 'Olexandr'


a0 = 1
a1 = 0.003
a2 = 0.0001
f0 = 220
f1 = 240
f2 = 230


def s(t):
    return a0 * cos(2*pi*f0*t) + a1 * cos(2*pi*f1*t) + a2 * cos(2*pi*f2*t)


def main():
    # wav = WavFile('resources/audio_files/files/examples/seven_.wav')
    plotter = Plotter()
    fd = 280
    n = 1024
    fs = 1000
    s_in = []
    for i in range(n):
        s_in.append(s(i))
    # fi_filter = Filter(window_name="hemming", fs=fs, fx=50, use_abs=False)
    # plotter.add_sub_plot_data("original", list(wav.samples))
    # l = list(numpy.fft.fft(wav.samples))
    # plotter.add_sub_plot_data("original_FFT", l)
    # plotter.add_sub_plot_data("filtered", fi_filter.finite_impulse_filter(10, in_data=l, fd=wav.frame_rate))

    plotter.add_sub_plot_data("original", list(map(abs, s_in)))
    plotter.add_sub_plot_data("original_FFT", list(numpy.fft.fft(s_in)))
    # plotter.add_sub_plot_data("filtered", fi_filter.finite_impulse_filter(n, in_data=numpy.fft.fft(s_in), fd=fd))

    plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    main()