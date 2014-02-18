from math import log10
import numpy
from algorithms.vad import VAD
from beans.WavFile import WavFile
from utils.Utils import get_files

__author__ = 'Olexandr'


class NBC:
    """
    Naive Bayes Classifier
    """

    def __init__(self, cf, eps=0.001, frame_size=10):
        self.cf = cf
        self.eps = eps
        self.frame_size = frame_size
        self.speech_class = {"energy": [], "mdf": [], "zcr": [], "sfm": []}
        self.non_speech_class = {"energy": [], "mdf": [], "zcr": [], "sfm": []}

        self.all_words_count, self.all_docs_count = 0, 0
        self.speech_words_count, self.non_speech_words_count = 0, 0

        self.speech_wave_files = WavFile.get_all_waves(get_files(cf.get("nbc", "path_to_speech_files"), ".wav"))
        self.non_speech_wave_files = WavFile.get_all_waves(get_files(cf.get("nbc", "path_to_non_speech_files"), ".wav"))

        self.speech_docs_count = len(self.speech_wave_files)
        self.non_speech_docs_count = len(self.non_speech_wave_files)
        self.all_docs_count = self.speech_docs_count + self.non_speech_docs_count

    def teach_classifier(self):
        self.speech_words_count += self.teach_one_class(self.speech_wave_files, self.speech_class)
        self.non_speech_words_count += self.teach_one_class(self.non_speech_wave_files, self.non_speech_class)
        self.all_words_count = self.speech_words_count + self.non_speech_words_count

    def teach_one_class(self, wav_files, class_characteristics):
        words_count = 0
        for i in wav_files:
            energy, mdf, zcr, sfm, items, speech = VAD.vad(i, frame_size=self.frame_size)
            self.teach(energy, class_characteristics["energy"])
            self.teach(mdf, class_characteristics["mdf"])
            self.teach(zcr, class_characteristics["zcr"])
            self.teach(sfm, class_characteristics["sfm"])
            words_count += len(energy)
        return words_count

    def teach(self, words, class_characteristic):
        for j in range(len(words)):
            idx, val = self.find_value(words[j], class_characteristic)
            if idx != -1:
                class_characteristic[idx] = (words[j], val + 1)
            else:
                class_characteristic.append((words[j], 1))

    def find_value(self, value, data_class):
        for i in range(len(data_class)):
            if abs(numpy.float64(value) - numpy.float64(data_class[i][0])) < self.eps:
                return i, data_class[i][1]
        return -1, 0

    def classifier(self, wav):
        energy, mdf, zcr, sfm, items, speech = VAD.vad(wav, frame_size=self.frame_size)
        speech_by_e = self.probability(self.speech_words_count, self.speech_docs_count,
                                       self.speech_wave_files["energy"], energy)
        speech_by_mdf = self.probability(self.speech_words_count, self.speech_docs_count, self.speech_wave_files["mdf"],
                                         mdf)
        speech_by_zcr = self.probability(self.speech_words_count, self.speech_docs_count, self.speech_wave_files["zcr"],
                                         zcr)
        speech_by_sfm = self.probability(self.speech_words_count, self.speech_docs_count, self.speech_wave_files["sfm"],
                                         sfm)

        non_speech_by_e = self.probability(self.non_speech_words_count, self.non_speech_docs_count,
                                           self.non_speech_wave_files["energy"], energy)
        non_speech_by_mdf = self.probability(self.non_speech_words_count, self.non_speech_docs_count,
                                             self.non_speech_wave_files["mdf"], mdf)
        non_speech_by_zcr = self.probability(self.non_speech_words_count, self.non_speech_docs_count,
                                             self.non_speech_wave_files["zcr"], zcr)
        non_speech_by_sfm = self.probability(self.non_speech_words_count, self.non_speech_docs_count,
                                             self.non_speech_wave_files["sfm"], sfm)

        return speech_by_e, speech_by_mdf, speech_by_sfm, speech_by_zcr, non_speech_by_e, non_speech_by_mdf,  non_speech_by_sfm, non_speech_by_zcr

    def probability(self, words_count, docs_count, class_characteristic, words):
        res = log10(docs_count / self.all_docs_count)
        for i in range(len(words)):
            idx, val = self.find_value(words[i], class_characteristic)
            res += log10((val + 1) / (self.all_words_count + words_count))
        return res