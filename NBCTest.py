import configparser as cp
from algorithms.naiveBayesClassifier.NBC import NBC
from beans.WavFile import WavFile

__author__ = 'Olexandr'


def main():
    cf = cp.ConfigParser()
    cf.read("properties/properties.cfg")
    nbc = NBC(cf)
    nbc.teach_classifier()
    speech_by_e, speech_by_mdf, speech_by_sfm, speech_by_zcr, non_speech_by_e, non_speech_by_mdf, non_speech_by_sfm, non_speech_by_zcr = nbc.classifier(
        WavFile("./resources/audio_files/waves/12345678910.wav"))

    if speech_by_e > non_speech_by_e:
        print("speech")
    else:
        print("non speech")

    if speech_by_mdf > non_speech_by_mdf:
        print("speech")
    else:
        print("non speech")

    if speech_by_sfm > non_speech_by_sfm:
        print("speech")
    else:
        print("non speech")

    if speech_by_zcr > non_speech_by_zcr:
        print("speech")
    else:
        print("non speech")


if "__main__" == __name__:
    main()