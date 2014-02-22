import wave
import os.path
import numpy as np
import matplotlib.pyplot as plot

from handlers import FFT

__author__ = 'Olexandr'


class WavFile:
    def __init__(self, file_name=None, frames=None, sample_width=None, time=0, word="anonymous"):
        """
        initialize WavFile object
        you can use name of file from file system
        or list of frames, sample_width and time, this variant good
            when you record audio yourself and don't want save it to disk
        @param file_name: name of file (if you use file from disk)
        @param frames: frames which represents wave file
        @param sample_width: width of samples
        @param time: length of recorded file in seconds
        """
        self.types = {1: np.int8, 2: np.int16, 4: np.int32}
        if file_name:
            if os.path.isfile(file_name):
                self.file_name = file_name
                wav = wave.open(file_name, mode="r")
                (self.number_of_channels, self.sample_width, self.frame_rate, self.number_of_frames, self.comp_type,
                    self.comp_name) = wav.getparams()
                self.file_size_sec = self.number_of_frames/self.frame_rate
                self.samples = np.fromstring(wav.readframes(self.number_of_frames), dtype=self.types[self.sample_width])
                # self.samples = [i/32768 for i in self.samples]
                wav.close()
            else:
                raise Exception("File '" + file_name + "' is not exists!")
        elif not (frames is None) and not(sample_width is None) and time > 0:
            self.file_name = word
            self.sample_width = sample_width
            self.samples = np.fromstring(frames, dtype=self.types[self.sample_width])
            self.file_size_sec = time
            self.number_of_channels = 2
        else:
            raise Exception("Wrong input data!")

    def get_one_channel_data(self, really_transform=False):
        """
        if file has one channel: return it
        else if really_transform true: return middle value of all channels
        else: return first channel (faster than middle value of all)
        @param really_transform:
        @return:
        """
        if self.number_of_channels == 1:
            return self.samples
        elif really_transform:
            channels = []
            one_channel_data = []
            for i in range(self.number_of_channels):
                channels.append(self.samples[i::self.number_of_channels])
            for i in range(len(channels[0])):
                data = 0
                for j in range(self.number_of_channels):
                    data += channels[j][i]
                one_channel_data.append(data/self.number_of_channels)
            return one_channel_data
        else:
            return self.samples[0::self.number_of_channels]

    def plot_samples_as_one_channel(self, show=True, save=False):
        """
        plot only one sample of file which returned by function get_one_channel_data()
        @param show: flag for showing figure
        @param save: flag for saving .png file with figure
        """
        one_channel = self.get_one_channel_data()
        time = np.linspace(0, self.file_size_sec, num=len(one_channel))
        plot.plot(time, one_channel, "g")
        plot.grid(True)
        plot.title(self.file_name)
        if save:
            plot.savefig(self.file_name + ".png")
        if show:
            plot.show()

    def plot_samples_all_channels(self, show=True, save=False):
        """
        plot all samples of file
        @param show: flag for showing figure
        @param save: flag for saving .png file with figure
        """
        for i in range(self.number_of_channels):
            channel = self.samples[i::self.number_of_channels]
            time = np.linspace(0, self.file_size_sec, num=len(channel))
            axes = plot.subplot(self.number_of_channels, 1, i+1)
            axes.plot(time, channel, "g")
            plot.grid(True)
            plot.title(self.file_name + " channel " + str(i))
        if save:
            plot.savefig(self.file_name + ".png")
        if show:
            plot.show()

    def plot_fft_of_wav(self, show=True, save=False, really_transform=False):
        """
        plot list with fft value for sample of file
        @param show: flag for showing figure
        @param save: flag for saving .png file with figure
        """
        fft = abs(FFT.fft_diff_len(self.get_one_channel_data(really_transform)))
        plot.plot(range(len(fft)), fft)
        plot.grid(True)
        plot.title(self.file_name + " fft")
        if save:
            plot.savefig(self.file_name + ".fft.png")
        if show:
            plot.show()

    def get_file_size_msec(self):
        return self.file_size_sec * 1000

    def get_simple_file_name(self):
        """
        get simple file name from path to file
        @return: file name (word)
        """
        word = self.file_name.lower()
        word = word[str(word).rfind("\\")+1:len(word)]
        word = word[str(word).rfind("/")+1:len(word)]
        return word[0:len(word)-4]

    @staticmethod
    def get_all_waves(files_list):
        """
        get all files from list and create list of WavFile objects
        @param files_list: list of paths to files
        @return: list of WavFile objects
        """
        waves = []
        for i in files_list:
            waves.append(WavFile(i))
        return waves

    def __str__(self):
        return self.get_simple_file_name() + ": " + str(self.file_size_sec) + " sec"