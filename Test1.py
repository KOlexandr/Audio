import math
import numpy
from algorithms.fir import FiniteImpulseFilter
from algorithms.harmonicOscillations import HarmonicOscillations
from beans.WavFile import WavFile
from handlers.Plotter import Plotter

__author__ = 'Olexandr'


a0 = 1
a1 = 1
a2 = 0.0001
f0 = 220
f1 = 222
f2 = 240


def s(t):
    return a0 * math.cos(2*math.pi*f0*t) + a1 * math.cos(2*math.pi*f1*t) + a2 * math.cos(2*math.pi*f2*t)


def normalize(data):
    coefficient = max(abs(data))
    return data/coefficient


def main():
    # plotter = Plotter()
    # fd = 280
    # n = 1024
    # fs = 1000
    # s_in = []
    # for i in range(n):
    #     s_in.append(2*pi*f0*i)

    # file = WavFile('resources/audio_files/files/nonSpeech/White_noise.wav')
    file = WavFile('algorithms/harmonicOscillations/audio/meandr25Hz.wav')
    freq, amplitude = HarmonicOscillations.fft_db_hz(file)
    # wav__samples = normalize(file.samples)
    wav__samples = file.samples
    p = abs(numpy.fft.rfft(wav__samples))

    plotter = Plotter()
    plotter.add_sub_plot_data("original", wav__samples)
    # e_ = list(map(lambda x: 20*math.log10(x + 1e-8), ))
    out = FiniteImpulseFilter.filter(amplitude, 100, file.frame_rate, 20, 50, "hemming")
    plotter.add_sub_plot_data("fft", amplitude, freq, scale_x='log', scale_y='log')
    plotter.add_sub_plot_data("fft_filter", out, freq, scale_x='log', scale_y='log')
    # plotter.add_sub_plot_data("fft_log", e_, scale_x='log')

    plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    main()