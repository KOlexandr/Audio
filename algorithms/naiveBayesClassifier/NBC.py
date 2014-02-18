from algorithms.naiveBayesClassifier.NBCUtils import find_value
from algorithms.vad import VAD

__author__ = 'Olexandr'


def teachProgramAndGetData(eps, frame_size):
    global allWordsCount, allDocsCount, speechClassE, speechClassF, speechClassZCR
    global nonSpeechClassE, nonSpeechClassF, nonSpeechClassZCR
    global speechWordsCount, nonSpeechWordsCount, speechDocsCount, nonSpeechDocsCount
    pathToSpeech = 'speech/'
    pathToNonSpeech = 'nonSpeech/'
    
    teachClassifier(pathToSpeech, pathToNonSpeech, eps, frame_size)
    
    sce = speechClassE
    scf = speechClassF
    scz = speechClassZCR
    awc = allWordsCount
    swc = speechWordsCount
    nswc = nonSpeechWordsCount
    adc = allDocsCount
    sdc = speechDocsCount
    nsdc = nonSpeechDocsCount
    nsce = nonSpeechClassE
    nscf = nonSpeechClassF
    nscz = nonSpeechClassZCR
    return sce, scf, scz, awc, swc, nswc, adc, sdc, nsdc, nsce, nscf, nscz


def teachClassifier(pathToSpeech, pathToNonSpeech, eps, frame_size)
    global allWordsCount, allDocsCount, speechClassE, speechClassF, speechClassZCR
    global nonSpeechClassE, nonSpeechClassF, nonSpeechClassZCR
    global speechWordsCount, nonSpeechWordsCount, speechDocsCount, nonSpeechDocsCount
    allWordsCount = 0 
    
    [listSpeech, listSpeechFs] = getWaveFiles(pathToSpeech)
    [speechWordsCount, speechClassE, speechClassF, speechClassZCR] = teachOneClass(listSpeech, listSpeechFs, eps, frame_size)
    speechDocsCount = listSpeech.size()
    allWordsCount = allWordsCount + speechDocsCount
    
    [listNoise, listFs] = getWaveFiles(pathToNonSpeech)
    [nonSpeechWordsCount, nonSpeechClassE, nonSpeechClassF, nonSpeechClassZCR] = teachOneClass(listNoise, listFs, eps, frame_size)
    nonSpeechDocsCount = listNoise.size()
    allWordsCount = allWordsCount + nonSpeechDocsCount
    allDocsCount = nonSpeechDocsCount + speechDocsCount
    
    
def teach_one_class(list_for_one_class, eps, frame_size):
    words_class_count = 0
    energy_class, mdf_class, zcr_class, sfm_class = [], [], [], []
    for i in list_for_one_class:
        energy, mdf, zcr, sfm, items_per_frame, speech = VAD.vad(i, frame_size=frame_size)
        energy_class = teach(energy, eps, energy_class)
        mdf_class = teach(mdf, eps, mdf_class)
        zcr_class = teach(zcr, eps, zcr_class)
        sfm_class = teach(sfm, eps, sfm_class)
        words_class_count += len(energy)
    return words_class_count, energy_class, mdf_class, zcr_class, sfm_class


def teach(data_list, eps, data_class):
    for j in range(len(data_list)):
        idx, val = find_value(data_list[j], data_class, eps)
        if idx != -1:
            data_class[idx][0] = data_list[j]
            data_class[idx][1] = val + 1
        else:
            data_class.append((data_list[j], 1))
    return data_class