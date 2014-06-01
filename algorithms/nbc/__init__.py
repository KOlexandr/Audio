from variables import path_to_speech, path_to_non_speech, path_to_test
from beans.ClassifierBean import ClassifierBean
from beans.WavFile import WavFile
from utils.Utils import get_files
from algorithms.vad import vad
from math import log10

__author__ = 'Olexandr'


class NBC:
    """
    Naive Bayes Classifier
    """

    def __init__(self, numbers_after_point=3, frame_size=20, extension=".wav", get_audio_files=WavFile.get_all_waves,
                 get_paths_to_files=get_files, used_characteristics=None, used_classes=None):
        """
        init method create object NBC with needle parameters
        @param numbers_after_point: value that use for make format of characteristics of audio signal
        @param frame_size: size of one frame (milliseconds) uses for analyze audio signal
        @param extension: extension of audio files which will be process by program for analyzing
        @param get_audio_files: function for get representation of audio files (function gets list of paths to files)
                            as default uses function for gets wav files? in future its may be mp3 files
        @param get_paths_to_files: function gets all paths to all files in inner folders of base path
                            (gets only files with given extension)
        @param used_characteristics: list with names of used characteristics of audio signal in VAD
        @param used_classes: classes of data which uses for classification (as default: "speech", "non_speech")
        function transform: transforms list of of file objects to list of pairs,
                            where first value is file object, second value - flag (True, False),
                            that means used or not this audio for teaching classifier
        """
        if not used_classes:
            used_classes = ["speech", "non_speech"]
        if not used_characteristics:
            used_characteristics = ["energy", "mdf", "zcr", "sfm"]

        self.extension = extension
        self.frame_size = frame_size
        self.used_classes = used_classes
        self.get_audio_files = get_audio_files
        self.get_paths_to_files = get_paths_to_files
        self.used_characteristics = used_characteristics

        self.all_words_count, self.all_docs_count = 0, 0
        self.data_class, self.docs_count, self.words_count, self.audio_files = {}, {}, {}, {}
        for j in used_classes:
            self.data_class[j] = {}
            self.audio_files[j] = []
            for i in used_characteristics:
                self.data_class[j][i] = {}
            self.docs_count[j], self.words_count[j] = 0, 0

        self.format_characteristic = lambda x: format(x, '.' + str(numbers_after_point) + 'f')
        self.transform = lambda l, flag: list(map(lambda x: ClassifierBean(x, flag), l))

    def add_audio_files(self, class_key, path_to_base_folder):
        """
        method append new representation of audio files to already existing files
        @param class_key: name of class which uses for classification
        @param path_to_base_folder: path to folder with audio files or with folders with files
        method counts new value of all_docs_count
        """
        self.audio_files[class_key] += self.transform(
            self.get_audio_files(self.get_paths_to_files(path_to_base_folder, self.extension)), False)
        self.docs_count[class_key] = len(self.audio_files[class_key])
        self.all_docs_count = 0
        for i in self.docs_count.keys():
            self.all_docs_count += self.docs_count[i]

    def add_one_audio_file(self, class_key, file_object=None, path_to_file=None):
        """
        method adds one audio file to existing files of some class
        @param class_key: name of class which uses for classification
        @param file_object: object which represent audio file (now WavFile)
        @param path_to_file: path to audio file
        method counts new value of all_docs_count
        """
        if not file_object is None:
            self.audio_files[class_key].append(ClassifierBean(file_object, False))
        elif not path_to_file is None:
            self.audio_files[class_key].append(ClassifierBean(self.get_audio_files([path_to_file])[0], False))
        else:
            raise Exception("One of parameters (file_object, path_to_file) should be not None")
        self.docs_count[class_key] += 1

    def teach_classifier(self):
        """
        method teach classifier for classes which uses for classification
        method counts new value of all_words_count
        """
        for i in self.used_classes:
            self.teach_one_class(i)
        self.all_words_count = 0
        for i in self.words_count.keys():
            self.all_words_count += self.words_count[i]

    def teach_one_class(self, class_key):
        """
        1. method runs VAD for each file which is not classified yet
        2. gets all needle characteristics which were set in init method
        3. runs teach method for each of characteristics
        @param class_key: name of active class of data
        """
        words_count = 0
        characteristics = self.data_class[class_key]
        for i in self.audio_files[class_key]:
            if not i.classified:
                parameters = vad(i.file_object, frame_size=self.frame_size)
                for j in self.used_characteristics:
                    self.teach(parameters.get(j), characteristics[j])
                words_count += parameters.get("words_count")
                i.classified = True
        self.words_count[class_key] += words_count

    def teach(self, words, characteristic):
        """
        method uses for teach classifier with using one selected characteristic
        @param words: list with values of one characteristic for each frame
        @param characteristic: dict with counts of same values for selected characteristic
        """
        if words is not None and characteristic is not None:
            for j in words:
                str_val = self.format_characteristic(j)
                if characteristic.get(str_val) is None:
                    characteristic[str_val] = 1
                else:
                    characteristic[str_val] += 1

    def classify(self, file):
        """
        classify given audio file as one of given classes
        @param file: audio file object
        @return: result of classification
        """
        result = {}
        current_characteristics = vad(file, frame_size=self.frame_size)
        for i in self.used_classes:
            result[i] = {}
            for j in self.used_characteristics:
                result[i][j] = self.probability(i, j, current_characteristics.get(j))
        return result

    def probability(self, class_key, characteristic_key, words):
        """
        finds probability audio file as one of given classes
        @param class_key: class name
        @param characteristic_key: characteristic name
        @param words: list with values of current characteristic for each frame
        @return: probability of None if words is None
        """
        if words is not None:
            res = log10(self.docs_count[class_key] / self.all_docs_count)
            characteristic = self.data_class[class_key][characteristic_key]
            for i in words:
                val = characteristic.get(self.format_characteristic(i))
                if val is None:
                    val = 0
                res += log10((int(val) + 1) / (self.all_words_count + self.words_count[class_key]))
            return res
        else:
            return None

    def get_classes(self, probabilities):
        """
        method find max probability for each characteristic
        @param probabilities: all found probabilities for all classes and characteristics
        @return: dict with all characteristics and name and value of class by each characteristic
        """
        classes = {}
        p_by_c = {}
        for j in self.used_characteristics:
            p_by_c[j] = {}
        for i in self.used_classes:
            for j in self.used_characteristics:
                p_by_c[j][i] = probabilities[i][j]
        for i in self.used_characteristics:
            classes[i] = {}
            val = max(p_by_c[i].values())
            for j in self.used_classes:
                if val == p_by_c[i][j]:
                    classes[i][j] = val
                    break
        return classes


def test():
    nbc = NBC()
    nbc.add_audio_files("speech", path_to_speech)
    nbc.add_audio_files("non_speech", path_to_non_speech)

    # nbc.add_one_audio_file("speech", path_to_file="E:\EmergencyFiles\Python\RecordAudio\\resources\\audio_files\isolated_digits\MAN\AE\\1A_endpt.wav")

    nbc.teach_classifier()
    classes = nbc.get_classes(nbc.classify(WavFile(path_to_test + "12345678910.wav")))
    print(classes)


if "__main__" == __name__:
    test()