#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# This file is part of Coruja-scripts
#
# Coruja-scripts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Coruja-scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Coruja-scripts.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2011 Grupo Falabrasil - http://www.laps.ufpa.br/falabrasil
#
# Author 2011: Pedro Batista - pedosb@gmail.com

import numpy as np
from matplotlib import pyplot as plt
from gist import peakdetect
from numpy.matlib import rand
from scipy.io import wavfile
from scipy import signal
from algorithms.lpc import lpc_signal


def lpc(s, m, p):
    x = s.get_frame(m)
    R = lambda k: auto_corr(x, k)
    a = np.zeros((p + 1, p + 1))
    k = np.zeros(p + 1)

    E = np.concatenate(([R(0)], np.empty(p)))
    for i in range(1, p + 1):
        c = 0
        for j in range(1, i):
            c += a[j, i - 1] * R(i - j)
        k[i] = (R(i) - c) / E[i - 1]

        a[i][i] = k[i]

        for j in range(1, i):
            a[j][i] = a[j][i - 1] - k[i] * a[i - j][i - 1]

        E[i] = (1 - k[i] ** 2) * E[i - 1]

    fa = np.empty(p + 1)
    fa[0] = 1
    for j in range(1, p + 1):
        fa[j] = -a[j][p]
    return fa, E[p]


def all_f0(s, f0_threshold=0.55, max_f0=300, pulse_duration=3, clip_threshold_percentage=0.4, lookahead=50):
    f0_list = np.empty(s.get_number_of_frames())
    for m, i in zip(s.get_frames_positions(), range(s.get_number_of_frames())):
        f0_list[i] = f0(s, m, f0_threshold, max_f0, pulse_duration, clip_threshold_percentage, lookahead)
    return f0_list


def f0(s, m, f0_threshold=0.5, max_f0=300, pulse_duration=3, clip_threshold_percentage=0.4, lookahead=50):
    x = s.get_frame(m)
    #   plt.subplot(211)
    #   plt.plot(x)
    clip_threshold = clip_threshold_percentage * max(x)
    x[x < clip_threshold] = 0
    x -= clip_threshold
    #   plt.plot(x)
    r = np.array([auto_corr(x, i) for i in range(0, len(s.window))])
    r = r / max(r)
    #   plt.subplot(212)
    #   plt.plot(r)
    min_lag = np.floor(s.fs / float(max_f0))

    max_peaks, _ = peakdetect.peakdetect(r, lookahead=lookahead)
    if len(max_peaks) != 0:
        x, y = zip(*max_peaks)
        #      plt.plot(x, y, 'o')
        y = np.array(y)
        max_index = y.argmax()
        max_peak = x[max_index], y[max_index]
        print(max_peak)
    else:
        max_peak = None

    if max_peak is not None:
        if max_peak[1] > f0_threshold:
            return s.fs / max_peak[0]
    return 0


def auto_corr(x, k):
    c = 0
    for n in range(0, len(x) - k):
        c += x[n] * x[n + k]
    return c


def lpc_encode(s, p):
    lpc_list = np.empty((s.get_number_of_frames(), p + 1), dtype=np.float16)
    f0_list = np.empty(s.get_number_of_frames(), dtype=np.uint16)
    e_list = np.empty(s.get_number_of_frames(), dtype=np.float32)
    for m, i in zip(s.get_frames_positions(), range(s.get_number_of_frames())):
        lpc_list[i], e_list[i] = lpc(s, m, p)
        print(e_list[i])
        f0_list[i] = f0(s, m)

    #   N = len(s.window)
    N = s.fs / s.frame_rate
    ss = np.zeros(len(s.data))
    zi = np.zeros(p)
    print(f0_list)
    an = False
    for ai, f0i, ei, i in zip(lpc_list, f0_list, e_list, range(len(f0_list))):
        if f0i == 0:
            x = rand(N) * np.sqrt(12)
            an = False
        else:
            x = np.zeros(N)
            x[range(0, N, int(np.floor(s.fs / f0i)))] = np.sqrt(ei) * 0.33
            if not an:
                zi = np.zeros(p)
            an = True
        #      q = np.zeros(N + 1, dtype=np.float128)
        #      u = np.zeros(N + 1, dtype=np.float128)
        #      for n in range(1, N + 1):
        #	 for k in range(1, p + 1):
        #	    if n - k > 0:
        #	       q[n] += ai[k] * q[n-k]
        #	       u[n] += ai[k] * u[n-k] + x[n-1]
        #	    else:
        #	       q[n] += ai[k] #* zi[abs(n-k)]
        #	       u[n] += x[n-1]
        #      poly = np.empty(3, dtype=np.float64)
        start = i * s.fs / s.frame_rate
        #      q = q[1:]
        #      u = u[1:]
        #      poly[0] = np.mean(u**2)
        #      poly[1] = np.mean(u * q)
        #      m = np.var(q) + np.mean(q)**2
        #      poly[2] = m - s.power(start)
        #      print poly
        #      g = np.roots(poly)
        #      if np.iscomplex(g).any() or (g <= 0).all():
        #	 g = 0
        #      else:
        #	 g = g[g>0]
        #      x = q + g * u
        sl, zi = signal.lfilter([1], ai, x, zi=zi)
        ss[start:start + N] += sl
    plt.plot(ss)
    return ss


if __name__ == '__main__':
    #   fs, data = wavfile.read('../../dtw-asr-python/wav/pedro.new/mundurucus_1.wav')
    fs, data = wavfile.read('ombro.wav')
    s = lpc_signal.Signal(data[13200:14200], fs, window=np.ones(400), frame_rate=100)
    plt.plot(300 * (s.data / float(max(s.data))))
    plt.figure()
    lpc_encode(s, 10)
    #   for m in s.get_frames_positions():
    #      plt.plot(m + 200, f0(s, m), 'og')
    #      pass
    plt.show()
