import configparser as cp
from algorithms.naiveBayesClassifier.NBC import NBC
from beans.WavFile import WavFile

__author__ = 'Olexandr'


def main():
    """
    cf: configurations parser, for get all parameters saved in configuration file
    """
    cf = cp.ConfigParser()
    cf.read("properties/properties.cfg")
    nbc = NBC()
    nbc.add_audio_files("speech", cf.get("nbc", "path_to_speech"))
    nbc.add_audio_files("non_speech", cf.get("nbc", "path_to_non_speech"))
    nbc.teach_classifier()
    classes = nbc.get_classes(nbc.classify(WavFile("./resources/audio_files/waves/12345678910.wav")))
    print(classes)


if "__main__" == __name__:
    main()