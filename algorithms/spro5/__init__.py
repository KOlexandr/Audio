from beans.WavFile import WavFile
from variables import path_to_project
from utils import Utils
import ctypes
import re
import os

__author__ = 'Olexandr'

path_to_dll = os.path.dirname(__file__) + "/"
path_to_mfcc = path_to_project + "/resources/mfcc/"


class SPro5:
    """
    Wrapper for http://habrahabr.ru/post/150251
    wrapper for SPro 5.0 c/c++ program
    use DLL for transform wav file to mfcc
    """
    def __init__(self):
        self.s_pro_5 = ctypes.CDLL(path_to_dll + "SProWrapper.dll")
        self.wr_s_pro_5 = ctypes.CDLL(path_to_dll + "WrapperWRSystemSPro.dll")
        self.mfcc = {}
        self.file_name = {"learn": "learn_base", "base": "test_base"}

    def s_pro_base_params(self, input_file, output_file):
        """
        runs SPro 5.0 with base parameters
        reads input wav file from path and transform it into mfcc file to another path
        """
        wav = WavFile(input_file)
        data = "--format=wave --sample-rate=" + str(wav.frame_rate) + " --mel --freq-min=0 --freq-max=8000" \
               " --channel=" + str(wav.number_of_channels) + " --fft-length=256 --length=16.0" \
               " --shift=10.0 --num-ceps=13 " + str(input_file) + " " + str(output_file)
        self.s_pro_5.main(len(data) * 2, ctypes.c_wchar_p(data))

    def s_pro_custom_params(self, parameters_str):
        """
        all possible parameters for run SPro 5.0
        @param parameters_str: string with all parameters in correct format
        """
        self.s_pro_5.main(len(parameters_str)*2, ctypes.c_wchar_p(parameters_str))

    @staticmethod
    def print_help():
        """
        prints help information about SPro 5.0
        and all possible parameters for using it
        """
        print("Usage: SPro [options] in_file out_file")
        print("Synopsis: Filter-bank based cepstral analysis of the input signal.")
        print("Options:")
        print("\t-F, --format=s            input signal file format (pcm16)")
        print("\t-f, --sample-rate=n       signal sample rate for pcm16 input (8000.0 Hz)")
        print("\t-x, --channel=n           channel number (1)")
        print("\t-B, --swap                swap sample byte order (don't)")
        print("\t-I, --input-bufsize=n     input buffer size in kbytes (10000)")
        print("\t-O, --output-bufsize=n    output buffer size in kbytes (10000)")
        print("\t-H, --header              output variable length header (don't)\n")
        print("\t-k, --pre-emphasis=f      pre-emphasis coefficient (0.95)")
        print("\t-l, --length=f            frame length in ms (20.0 ms)")
        print("\t-d, --shift=f             frame shift in ms (10.0 ms)")
        print("\t-w, --window=s            weighting window (HAMMING)\n")
        print("\t-n, --num-filter=n        number of filters in the filter-bank (24)")
        print("\t-a, --alpha=f             frequency warping parameter (0.0)")
        print("\t-m, --mel                 use MEL frequency scale (off)")
        print("\t-i, --freq-min=n          lower frequency bound (0 Hz)")
        print("\t-u, --freq-max=n          higher frequency bound (Fs/2)")
        print("\t-b, --fft-length=n        FFT length (512)\n")
        print("\t-p, --num-ceps=n          number of cepstral coefficients (12)")
        print("\t-r, --lifter=n            liftering value (0)\n")
        print("\t-e, --energy              add log-energy (off)")
        print("\t-s, --scale-energy=f      scale and normalize log-energy (off)\n")
        print("\t-Z, --cms                 cepstral mean normalization")
        print("\t-R, --normalize           variance normalization")
        print("\t-L, --segment-length=n    segment length in frames for normalization (whole data)")
        print("\t-D, --delta               add first order derivatives")
        print("\t-A, --acceleration        add second order derivatives")
        print("\t-N, --no-static-energy    remove static energy\n")
        print("\t-v, --verbose             verbose mode")
        print("\t-V, --version             print version number and exit")
        print("\t-h, --help                this help message\n")

    def store_mfcc_file_data(self):
        """
        gets all *.mfcc files from resources/mfcc/base folder
        and save all data in self.mfcc dict
        """
        file_paths = Utils.get_simple_file_names(path_to_mfcc + "base", ".mfcc")
        words = []
        for i in file_paths:
            word = re.sub("-[0-9]{1,3}\\.mfcc$", "", str(i).lower())
            if not word in self.mfcc:
                self.mfcc[word] = []
            self.mfcc[word].append(i)
            if not word in words:
                words.append(word)

    def write_mfcc_data_to_file(self, file_name):
        """
        writes self.mfcc into .txt file
        @param file_name: WrapperWRSystemSPro will work with this file
        @return:
        """
        f = open(file_name + ".txt", "w")
        f.write(str(len(self.mfcc)) + "\n")
        for i in self.mfcc.keys():
            f.write(str(i).lower() + "\n")
            f.write(str(len(self.mfcc[i])) + "\n")
            for j in self.mfcc[i]:
                f.write(j + "\n")
        f.close()

    def waves_files_to_mfcc(self):
        """
        gets all wav files in dir and transforms each of them into mfcc
        """
        file_paths = Utils.get_simple_file_names(path_to_mfcc + "waves", ".wav")
        leading_zeros = len(str(len(file_paths)))
        for i in range(len(file_paths)):
            output_file = re.sub("\\.wav", "-" + str(i + 1).zfill(leading_zeros) + ".mfcc", file_paths[i])
            self.s_pro_base_params(path_to_mfcc + "waves/" + file_paths[i], path_to_mfcc + "base/" + output_file)

    def wr_system(self, work_type):
        """
        runs WrapperWRSystemSPro
        @param work_type: ['learn', 'base']
            'learn': for learning system
            'base': for testing system
        base_file: base file name - file with list of mfcc files and words
        system_file: system result file
        wer_file: WER (Word Error Rate) file
        """
        # self.waves_files_to_mfcc()
        # self.store_mfcc_file_data()
        # self.write_mfcc_data_to_file(path_to_mfcc + "base/" + base_file)
        params = [
            "--" + str(work_type),
            "--base " + path_to_mfcc + "base/" + self.file_name[work_type] + ".txt",
            "--system " + path_to_mfcc + "results/system.bin",
            "--test_results " + path_to_mfcc + "results/wer_" + self.file_name[work_type] + ".txt"
        ]
        if "base" == work_type:
            joined_params = ' '.join(params[1:])
        else:
            joined_params = ' '.join(params)
        self.wr_s_pro_5.main(len(joined_params)*2, ctypes.c_wchar_p(joined_params))


if "__main__" == __name__:
    s = SPro5()
    s.wr_system("learn")