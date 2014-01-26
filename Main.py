__author__ = 'Olexandr'

import Utils
import Record
from WavFile import WavFile


dict_with_fft, length = Utils.process_examples("examples")

while True:
    time = 2
    wav_file = Record.record_and_get_wav(time)
    test = Utils.process_one_wav(wav_file, length)
    print(Utils.corrcoef(dict_with_fft, test))