__author__ = 'Olexandr'

import wave
import pyaudio
from WavFile import WavFile

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100


def record_audio_to_file(time, file_name):
    sample_width, frames = record_audio(time)
    wf = wave.open(file_name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(frames)
    wf.close()


def record_audio(time):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []
    for i in range(0, int(RATE / CHUNK * time)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()
    return p.get_sample_size(FORMAT), b''.join(frames)


def record_and_get_wav(time):
    sample_width, frames = record_audio(time)
    return WavFile(frames=frames, sample_width=sample_width, time=time)