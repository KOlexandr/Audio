import math
from vad.VADUtils import energy_logarithm, zero_crossing_rate

__author__ = 'Olexandr'

"""
Voice Activity Detection
"""


def vad(wav_file, frame_size=10):
    frame_count = int(wav_file.get_file_size_msec()/frame_size)
    items_per_frame = math.floor(len(wav_file.samples)/frame_count)
    
    energy_prim_thresh = 40
    f_prim_thresh = 185
    zcr_prim_thresh = 5
    
    silence_count = 0
    energy, f, zcr, speech = [], [], [], []
    
    for i in range(frame_count):
        sub = wav_file.samples[i*items_per_frame+1:(i+1)*items_per_frame]
        energy.append(energy_logarithm(sub))
        f.append(max(sub))
        zcr.append(zero_crossing_rate(sub))
        
        min_energy = min(energy)
        min_f = min(f)
        min_zcr = min(zcr)
        
        if min_energy < 0:
            min_energy = 0.001
        thresh_energy = energy_prim_thresh * math.log(min_energy)
        thresh_f = f_prim_thresh
        thresh_zcr = zcr_prim_thresh
        
        counter = 0
        if (energy[i] - min_energy) >= thresh_energy:
            counter += 1
        if (f[i] - min_f) >= thresh_f:
            counter += 1
        if (zcr[i] - min_zcr) >= thresh_zcr:
            counter += 1

        if counter > 1:
            speech.append(1)
        else:
            speech.append(0)
            silence_count += 1
        # if speech[i] == 0:
        #     min_energy = (silence_count*min_energy+energy[i])/(silence_count+1)
        # thresh_energy = energy_prim_thresh*math.log(min_energy)
    return energy, f, zcr, items_per_frame