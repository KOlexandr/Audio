import scipy
from pylab import *
from handlers.Plotter import Plotter

__author__ = 'Olexandr'


a0 = 1
a1 = 1
a2 = 0.0001
f0 = 220
f1 = 222
f2 = 240


def s(t):
    return a0 * cos(2*pi*f0*t) + a1 * cos(2*pi*f1*t) + a2 * cos(2*pi*f2*t)


def main():
    plotter = Plotter()
    fd = 280
    n = 1024
    fs = 1000
    s_in = []
    for i in range(n):
        s_in.append(2*pi*f0*i)
    # fi_filter = Filter(window_name="hemming", fs=fs, fx=50, use_abs=False)

    p = scipy.fft(s_in)

    plot(20 * log10(p + 0.000001), color='k')
    xlabel('Frequency (kHz)')
    ylabel('Power (dB)')
    show()
    # plotter.add_sub_plot_data("original", s_in)
    # plotter.add_sub_plot_data("original_FFT", list(fft))
    # plotter.add_sub_plot_data("filtered", fi_filter.finite_impulse_filter(n, in_data=numpy.fft.fft(s_in), fd=fd))

    # plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    main()