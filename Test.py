import numpy
import math
import scipy
from beans.WavFile import WavFile
from handlers.Plotter import Plotter

__author__ = 'Olexandr'

# WavFile.write("test.wav", buffer, 1)

# p = scipy.fft(buffer)
# from pylab import *
#
# plot(10 * log10(p + 0.000001), color='k')
# xlabel('Frequency (kHz)')
# ylabel('Power (dB)')
# show()

# plotter = Plotter()
# plotter.add_sub_plot_data("data", buffer)
# plotter.add_sub_plot_data("fft", db, scale_x='log')
# plotter.sub_plot_all_horizontal()


def fft_make(pow_of_2, size, reverse=False):
    pow_of_2 = int(pow_of_2)
    n = 1 << pow_of_2
    w = (2.0 * math.pi) / float(n)
    f = 0.0
    array_of_rotate = [0]*size
    if reverse:
        coef = -1
    else:
        coef = 1
    for _ in range(n):
        array_of_rotate.append(math.cos(f))
        array_of_rotate.append(coef * math.sin(f))
        f += w
    return array_of_rotate


def fft_binary_inversion(pow_of_2, i):
    j = 0
    while pow_of_2 > 0:
        j <<= 1
        j |= i & 1
        i >>= 1
        pow_of_2 -= pow_of_2
    return j


def fft_calc(pow_of_2, array_of_rotate, in_data, norm):
    pow_of_2 = int(pow_of_2)
    n = 1 << pow_of_2
    n2 = n >> 1
    out = [0]*len(in_data)

    for i in range(n):
        j = fft_binary_inversion(pow_of_2, i) << 1
        k = i << 1
        out[k] = in_data[j]
        out[k+1] = in_data[j+1]
        out[j] = in_data[k]
        out[j+1] = in_data[k+1]

    for i in range(pow_of_2):
        m = 1 << (i + 1)
        r = m << 1
        nom = 0
        k = 0
        y = 0
        z = 0
        h = 1 << (pow_of_2 - i)

        for j in range(n2, 0, -1):
            if k >= m:
                k = y = 0
                nom += r
                z = nom

            re = array_of_rotate[y]
            im = array_of_rotate[y+1]

            re2 = out[z+m]
            im2 = out[z+m+1]

            re1 = re2 * re - im2 * im
            im1 = im2 * re + re2 * im

            re2 = out[z]
            im2 = out[z+1]

            out[z] = im2 + im1
            out[z+m] = im2 - im1
            out[z-1] = re2 + re1
            out[z+m-1] = re2 - re1

            k += 2
            z += 2
            y += h

    if norm:
        re = 1.0 / float(n)
        for i in range(2*n):
            out[i] *= re
    return out


def main():
    wav = WavFile('test.wav')
    p2 = math.log2(wav.samples.nbytes/wav.sample_width)
    array_size = 1 << int(math.log2(wav.samples.nbytes/wav.sample_width))
    in_data = [0]*(array_size*2)
    for i in range(min(array_size*2, len(wav.samples))):
        in_data[i] = wav.samples[i]
    # c = fft_make(p2, array_size*2)
    # out = fft_calc(p2, c, in_data, True)
    out = abs(scipy.fft(in_data))

    delta = float(wav.frame_rate)/float(array_size)
    cur_freq = 0

    ampl = [0]*(array_size*2)

    max_val = -1000000
    start_max = False
    pos_max = 0
    for i in range(0, array_size, 2):
        ampl[i] = cur_freq
        ampl[i+1] = math.sqrt(out[i]*out[i]+out[i+1]*out[i+1])

        if ((ampl[i+1] - 160) > 0) and not start_max:
            start_max = True
            max_val = ampl[i+1]
            pos_max = i

        if start_max:
            if (ampl[i+1] - 160) > 0:
                if ampl[i+1] > max_val:
                    max_val = ampl[i+1]
                pos_max = i
            else:
                print("Max Freq = " + str(ampl[pos_max]) + ",  amp = " + str(ampl[pos_max+1]))
                start_max = 0

        cur_freq += delta
    plotter = Plotter()
    plotter.add_sub_plot_data("data", ampl)
    plotter.sub_plot_all_horizontal()

main()