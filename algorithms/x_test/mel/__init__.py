from algorithms.harmonicOscillations import HarmonicOscillations
from algorithms.fir import FiniteImpulseFilter
from variables import path_to_project
from handlers.Plotter import Plotter
from beans.WavFile import WavFile
import math

__author__ = 'Olexandr'

path_to_audio = path_to_project + "/resources/audio_files/test/"


class MFCC:
    def __init__(self, sample_rate, sample_per_frame, num_cepstra, num_mel_filters=30, pre_emphasis_alpha=0.95,
                 lower_filter_frequency=80.0):
        self.num_mel_filters = num_mel_filters
        self.pre_emphasis_alpha = pre_emphasis_alpha
        self.lower_filter_frequency = lower_filter_frequency

        self.dct = DCT(num_cepstra, num_mel_filters)
        self.bin = []
        self.num_cepstra = num_cepstra
        self.sample_rate = sample_rate
        self.sample_per_frame = sample_per_frame
        self.upper_filter_frequency = sample_rate / 2.0

    def doMFCC(self, framed_signal):
        #Magnitude Spectrum
        bin = self.magnitude_spectrum(framed_signal)
        framed_signal = self.pre_emphasis(framed_signal)
        #cbin=frequencies of the channels in terms of FFT bin indices (cbin[i]
        #for the i -th channel)
        
        #prepare filter for for melFilter
        #same for all
        cbin = self.fft_bin_indices()
        #process Mel Filterbank
        fbank = self.mel_filter(bin, cbin)
        #magnitude_spectrum and bin filter indices
        
        #Non-linear transformation
        f = self.non_linear_transformation(fbank)

        #Cepstral coefficients, by DCT
        return self.dct.perform_DCT(f)

    def pre_emphasis(self, input_signal):
        """
        emphasize high freq signal
        """
        output_signal = []
        #apply pre-emphasis to each sample
        for i in range(1, len(input_signal)):
                output_signal.append(float(input_signal[i] - self.pre_emphasis_alpha * input_signal[i - 1]))
        return output_signal

    def fft_bin_indices(self):
        cbin = [int(self.lower_filter_frequency / self.sample_rate * self.sample_per_frame)]
        # from cbin1 to cbin23
        for i in range(1, self.num_mel_filters+1):
            # center freq for i th filter
            fc = self.center_frequency(i)
            cbin.append(int(fc / self.sample_rate * self.sample_per_frame))
        cbin.append(self.sample_per_frame / 2)
        return cbin

    def center_frequency(self, i):
            mel_f_low = self.freq_to_mel(self.lower_filter_frequency)
            mel_f_high = self.freq_to_mel(self.upper_filter_frequency)
            temp = mel_f_low + ((mel_f_high - mel_f_low) / (self.num_mel_filters + 1)) * i
            return self.inverse_mel(temp)

    @staticmethod
    def non_linear_transformation(fbank):
        """
        performs nonlinear transformation
        @param fbank:
        @return: log of filter bac
        """
        f = []
        FLOOR = -50
        for i in range(len(fbank)):
            tmp = math.log(fbank[i])
            #check if ln() returns a value less than the floor
            if tmp < FLOOR:
                tmp = FLOOR
            f.append(tmp)
        return f

    def mel_filter(self, bin, cbin):
        """
        performs mel filter operation
        @param bin: magnitude spectrum (| |)^2 of fft
        @param cbin: mel filter coeffs
        @return: mel filtered coeffs--> filter bank coefficients.
        """
        temp = []
        for k in range(1, self.num_mel_filters+1):
            num1, num2 = 0.0, 0.0
            for i in range(cbin[k - 1], cbin[k]+1):
                num1 += ((i - cbin[k - 1] + 1) / (cbin[k] - cbin[k - 1] + 1)) * bin[i]

            for i in range(cbin[k]+1, cbin[k + 1]+1):
                num2 += (1 - ((i - cbin[k]) / (cbin[k + 1] - cbin[k] + 1))) * bin[i]
            temp.append(num1 + num2)
        fbank = []
        for i in range(self.num_mel_filters):
            fbank.append(temp[i + 1])
        return fbank
    
    def magnitude_spectrum(self, frame):
        #calculate FFT for current frame
        #calculate magnitude spectrum
        freq, amplitude = HarmonicOscillations.fft_db_amplitude(frame, 2, self.sample_per_frame, self.sample_rate)
        return amplitude

    @staticmethod
    def inverse_mel(x):
        return 700 * (10**(x / 2595) - 1)

    @staticmethod
    def freq_to_mel(freq):
            return 2595 * math.log10(1 + freq / 700)

    # @staticmethod
    # def freq_to_mel(freq):
    #     return list(map(lambda x: 1127.01048 * math.log(1 + x / 700), freq))

    # @staticmethod
    # def mel_to_freq(mel):
    #     return list(map(lambda x: math.e ** (x / 1127.01048) - 1, mel))


class DCT:
    
    def __init__(self, num_cepstra, m):
        """
        performs Inverser Fourier Transform
        we used Dct because there is only real coeffs
        @param num_cepstra: number of mfcc coeffs
        @param m: number of Mel Filters
        """
        self.m = m
        self.num_cepstra = num_cepstra
        
    def perform_DCT(self, y):
        cepc = [0]*self.num_cepstra
        #perform DCT
        for n in range(1, self.num_cepstra+1):
            for i in range(1, self.m+1):
                cepc[n - 1] += y[i - 1] * math.cos(math.pi * (n - 1) / self.m * (i - 0.5))
        return cepc


def test():
    file = WavFile(path_to_audio + "meandr25Hz.wav")
    freq, amplitude = HarmonicOscillations.fft_db_amplitude_wav(file)
    out = FiniteImpulseFilter.filter(amplitude, 10, file.frame_rate, 20, 50, "hemming")

    mfcc = MFCC(file.samples, file.number_of_frames, 10)
    plotter = Plotter()
    plotter.add_sub_plot_data("original", file.samples)
    plotter.add_sub_plot_data("fft_filtered", out, freq, scale_x='log', scale_y='log')
    plotter.add_sub_plot_data("mel", mfcc.doMFCC(freq))
    plotter.sub_plot_all_horizontal()


if "__main__" == __name__:
    test()