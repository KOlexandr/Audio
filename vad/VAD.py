import math
import numpy
from vad import VADUtils

__author__ = 'Olexandr'

"""
Voice Activity Detection
"""


def vad(wav_file):
    items_per_frame = math.floor(len(wav_file.samples)/wav_file.number_of_frames)
    
    energy_prim_thresh = 40
    f_prim_thresh = 185
    zcr_prim_thresh = 5
    
    silence_count = 0
    energy, f, zcr, speech = [], [], [], []
    
    for i in range(wav_file.number_of_frames):
        start_idx = (i-1)*items_per_frame+1
        end_idx = i*items_per_frame
        sub = wav_file.samples[start_idx:end_idx]
        energy.append(VADUtils.energy_logarithm(sub))
        f.append(max(sub))
        zcr.append(VADUtils.zero_crossing_rate(sub))
        
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
            speech[i] = 1
        else:
            silence_count += 1
        if speech[i] == 0:
            min_energy = (silence_count*min_energy+energy[i])/(silence_count+1)
        thresh_energy = energy_prim_thresh*math.log(min_energy)
    return energy, f, zcr, items_per_frame