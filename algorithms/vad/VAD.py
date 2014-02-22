import numpy
from math import log10, floor
from algorithms.vad.VADUtils import energy_logarithm, zero_crossing_rate, sfm


__author__ = 'Olexandr'


def vad(wav_file, frame_size=10, fft_function=numpy.fft.fft):
    """
    Voice Activity Detection (http://habrahabr.ru/post/192954)
    @param wav_file: WavFile object
    @param frame_size: size of one frame in milliseconds
    @param fft_function: function for count FFT
    @return: tuple of next parameters
            energy          - Short-term energy for each frame,                      (MatLab)
            freq_component  - Most Dominant Frequency Component for each frame,      (MatLab)
            zcr             - Zero Crossing Rate for each frame,                     (MatLab)
            sfm_list        - Spectral Flatness Measure for each frame,              (new)
            items_per_frame - items in one frame,                                    (MatLab)
            speech          - list with flags for each frame (silence or speech)     (new)
    """
    data = wav_file.get_one_channel_data()
    frame_count = int(wav_file.get_file_size_msec() / frame_size)
    items_per_frame = floor(len(data) / frame_count)

    #Threshold for Energy
    energy_prim_threshold = 40
    #Threshold for Most Dominant Frequency Component (Hz)
    freq_prim_threshold = 185
    #Threshold for Spectral Flatness Measure
    sfm_prim_threshold = 5
    #Threshold for Zero Crossing Rate
    zcr_prim_threshold = 20

    silence_count = 0
    thresh_energy, thresh_zcr, thresh_freq, thresh_sfm = 0, 0, 0, 0
    energy, zcr, freq_component, sfm_list, speech = [], [], [], [], []

    j = 0
    for i in range(frame_count):
        sub = data[i * items_per_frame:(i + 1) * items_per_frame]

        energy.append(energy_logarithm(sub))
        zcr.append(zero_crossing_rate(sub))
        freq_component.append(max(sub))

        sfm_list.append(sfm(abs(fft_function(sub))))

        min_energy = min(energy)
        min_zcr = min(zcr)
        min_freq = min(freq_component)
        min_sfm = min(sfm_list)

        if min_energy < 0:
            min_energy = 0.001

        if j < 5:
            thresh_energy = energy_prim_threshold * log10(min_energy)
            thresh_zcr = zcr_prim_threshold
            thresh_freq = freq_prim_threshold
            thresh_sfm = sfm_prim_threshold

        counter = 0
        if (energy[i] - min_energy) >= thresh_energy:
            counter += 1
        if (zcr[i] - min_zcr) >= thresh_zcr:
            counter += 1
        # if (freq_component[i] - min_freq) >= thresh_freq:
        #     counter += 1
        if (sfm_list[i] - min_sfm) >= thresh_sfm:
            counter += 1

        if counter > 1:
            speech.append(1)
        else:
            speech.append(0)
            silence_count += 1

        if speech[i] == 0:
            min_energy = (silence_count * min_energy + energy[i]) / (silence_count + 1)
        thresh_energy = energy_prim_threshold * log10(min_energy)

    return {"energy": energy,
            "mdf": freq_component,
            "zcr": zcr,
            "sfm": sfm_list,
            "items_per_frame": items_per_frame,
            "speech": speech,
            "words_count": len(energy)}