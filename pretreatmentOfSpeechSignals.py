import math
import numpy
import scipy
from beans.WavFile import WavFile
from handlers.Plotter import Plotter

__author__ = 'Olexandr'

signal = WavFile('test.wav').samples
plotter = Plotter()
plotter.add_sub_plot_data("original", signal)

# signal: fdyscr=16 KHz, 16 bit
# acoustic preprocessing of signal

d = len(signal)
tim = 1
i = 0
while i < d - 408:
    # block processing result - acoustic vector
    y = signal[i:i + 408]

    x = [0]
    for j in range(1, 408):
        #premphasis
        x.append(y[j] - y[j - 1])

    # pi=3.14
    z = []
    for j in range(408):
        #Hamming window
        z.append((0.54 - 0.46 * math.cos(2 * math.pi * (j - 1) / 408)) * x[j])
    c = abs(numpy.fft.rfft(z, 512))
    # amplitudes
    s = c[1:256]

    # binning of 255 spectral values amplitudes, j=2,3,...,256
    f = [0, 74.24, 156.4, 247.2, 347.6, 458.7, 581.6, 717.5, 867.9, 1034, 1218, 1422, 1647, 1895, 2171, 2475, 2812, 3184,
         3596, 4052, 4556, 5113, 5730, 6412, 7166, 8000]

    # krok=31,25
    krok = 16000 / 512
    a = [0] * 26
    j = 2
    k = 1
    n = [0] * 26
    h = krok * (j - 1)

    while k < 26:
        while f[k] < h < f[k + 1]:
            # interval [f(k),f(k+1)]
            alfa = (h - f[k]) / (f[k + 1] - f[k])
            a[k + 1] += s[j] * alfa
            n[k + 1] += 1
            a[k] += s[j] * (1 - alfa)
            n[k] += 1
            j += 1
            h = krok * (j - 1)
        a[k] /= n[k]+0.000001
        k += 1

        o = a[2:25]
        #O(tim,25)=sum(y.^2)
        # norma(tim) = norm(o[tim, 1:24))
        i += 160
        tim += 1  # next block
time = tim - 1

# normamax = max(norma[1:time])
# O(1:time, 1:24)= O(1:time, 1:24) / normamax  # normalization
# end of signal acoustic preprocessing

plotter.add_sub_plot_data('409 values', y)
plotter.add_sub_plot_data('premphasis', x)
plotter.add_sub_plot_data('Hemming', z)
plotter.add_sub_plot_data('512 fft', c)
plotter.add_sub_plot_data('256 elements', s)
plotter.sub_plot_all_horizontal()
# plot(O(time, 1:24))title('24-element vector')