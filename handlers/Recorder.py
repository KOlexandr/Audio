from beans.WavFile import WavFile
import pyaudio
import wave

__author__ = 'Olexandr'


class Recorder:
    """
    class record audio from microphone in different ways
    """
    def __init__(self, chunk=1024, rate=44100, channels=2, data_format=pyaudio.paInt16):
        self.chunk = chunk
        self.rate = rate
        self.channels = channels
        self.format = data_format

    def record_audio_to_file(self, time, file_name):
        """
        records audio and save as *.wav file
        @param time: time for record is seconds
        @param [str] file_name: name of new file
        """
        sample_width, frames = self.record_audio(time)
        wf = wave.open(file_name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.rate)
        wf.writeframes(frames)
        wf.close()

    def record_audio_to_file_and_get_wav(self, time, file_name):
        """
        records audio and save as *.wav file
        @param time: time for record is seconds
        @param file_name: name of new file
        @return WavFile object
        """
        sample_width, frames = self.record_audio(time)
        wf = wave.open(file_name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.rate)
        wf.writeframes(frames)
        wf.close()
        return WavFile(frames=frames, sample_width=sample_width, time=time, word=file_name)

    def record_audio(self, time):
        """
        records audio and returns recorded samples
        @param time: time for record is seconds
        @return: array of samples
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        print("* recording")

        frames = []
        for i in range(0, int(self.rate / self.chunk * time)):
            data = stream.read(self.chunk)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()
        return p.get_sample_size(self.format), b''.join(frames)

    def record_and_get_wav(self, time):
        """
        uses method record_audio and create new WavFile object from recorded samples
        @param time: time for record is seconds
        @return: WavFile object
        """
        sample_width, frames = self.record_audio(time)
        return WavFile(frames=frames, sample_width=sample_width, time=time)