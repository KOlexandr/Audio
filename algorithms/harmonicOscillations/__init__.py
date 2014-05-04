import math
import numpy
import ctypes
from beans.WavFile import WavFile
from handlers.Plotter import Plotter

__author__ = 'Olexandr'


path_to_dll = "algorithms/harmonicOscillations/HarmonicOscillations.dll"


class HarmonicOscillations:
    """
    http://habrahabr.ru/post/219337
    """

    @staticmethod
    def fft(wav):
        """
        wrapper for c++ fft from HarmonicOscillations.dll
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
    def fft_db_hz(wav):
        """
        wrapper for c++ fft_db_hz from HarmonicOscillations.dll
        create freq and amplitude vectors in c++-code (works more faster then HarmonicOscillations.fft)
        @param wav: custom WavFile
        @return: freq - vector of frequency (Hz), amplitude - vector of amplitudes (db)
        """
        dll = ctypes.CDLL(path_to_dll)
        p2 = int(math.log2(wav.samples.nbytes/wav.sample_width))
        array_size = 1 << p2
        in_data = (ctypes.c_double * (array_size*2))()
        freq = (ctypes.c_double * array_size)()
        amplitude = (ctypes.c_double * array_size)()

        min_size = min(array_size * 2, len(wav.samples))
        in_data[0:min_size] = wav.samples[0:min_size]

        dll.fft_db_hz(ctypes.c_int(p2), ctypes.c_int(wav.frame_rate), in_data, freq, amplitude)

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


def test():
    wav = WavFile('audio/sin100Hz.wav')
    freq, amplitude = HarmonicOscillations.fft(wav)
    freq1, amplitude1 = HarmonicOscillations.fft_db_hz(wav)

    plotter = Plotter()
    plotter.add_sub_plot_data("data", wav.samples)
    plotter.add_sub_plot_data("fft_log_fft", amplitude, freq, scale_x='log', scale_y='log')
    plotter.add_sub_plot_data("fft_log_fft_db_hz", amplitude1, freq1, scale_x='log', scale_y='log')

    plotter.sub_plot_all_horizontal()


def test_all_audio():
    sin = WavFile('audio/sin100Hz.wav')
    noise = WavFile('audio/noise.wav')
    m = WavFile('audio/meandr25Hz.wav')
    freq_sin, amplitude_sin = HarmonicOscillations.fft_db_hz(sin)
    freq_noise, amplitude_noise = HarmonicOscillations.fft_db_hz(noise)
    freq_m, amplitude_m = HarmonicOscillations.fft_db_hz(m)

    plotter = Plotter()
    plotter.add_sub_plot_data("sin 100 Hz", sin.samples)
    plotter.add_sub_plot_data("fft sin 100 Hz", amplitude_sin, freq_sin, scale_x='log', scale_y='log')
    plotter.add_sub_plot_data("noise", noise.samples)
    plotter.add_sub_plot_data("fft noise", amplitude_noise, freq_noise, scale_y='log')
    plotter.add_sub_plot_data("meandr25Hz", m.samples)
    plotter.add_sub_plot_data("fft meandr 25 Hz", amplitude_m[0:2500], freq_m[0:2500], scale_y='log')

    plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    # test()
    test_all_audio()