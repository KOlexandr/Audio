import numpy as np

from beans.WavFile import WavFile
from handlers.Processor import Processor

__author__ = 'Olexandr'


def main():
    processor = Processor("examples", np.fft.fft,
                          lambda: WavFile("waves/silenceSmall.wav").get_one_channel_data())
    processor.recorder.record_audio_to_file(3, "test1.wav")
    wav = WavFile("waves/13245678109Speed.wav")
    wav = WavFile("test1.wav")
    wav.plot_samples_as_one_channel()
    samples, word_count, max_len = processor.find_word_in_test_file(wav.get_one_channel_data())
    print("All words in file = " + str(word_count))
    for j in samples:
        word, coefficient = processor.lib.find_max_corrcoef_and_word(j, max_len)
        if coefficient > 0.3:
            print(word + " - " + str(coefficient))

if "__main__" == __name__:
    main()