import numpy as np
from WavFile import WavFile
from Processor import Processor

__author__ = 'Olexandr'


def main():
    processor = Processor("examples", np.fft.fft,
                          lambda: WavFile("waves/silenceSmall.wav").get_one_channel_data())
    # processor.recorder.record_audio_to_file(5, "test.wav")
    wav = WavFile("test.wav")
    wav.plot_samples_as_one_channel()
    samples, word_count, max_len = processor.find_word_in_test_file(wav.get_one_channel_data())
    print("All words in file = " + str(word_count))
    for j in samples:
        word, coefficient = processor.lib.find_max_corrcoef_and_word(j, max_len)
        if coefficient > 0.3:
            print(word + " - " + str(coefficient))


if "__main__" == __name__:
    main()