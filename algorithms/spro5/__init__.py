from variables import path_to_mfcc, path_to_mfcc_dll
from beans.WavFile import WavFile
from utils import Utils
import ctypes
import re
import os

__author__ = 'Olexandr'


class SPro5:
    """
    Wrapper for http://habrahabr.ru/post/150251
    wrapper for SPro 5.0 c/c++ program
    use DLL for transform wav file to mfcc
    """
    def __init__(self, path_to_dll):
        self.mfcc = {"learn": {}, "test": {}}
        self.ws_pro_5 = ctypes.CDLL(path_to_dll + "SPro.dll")
        self.s_pro_5 = ctypes.CDLL(path_to_dll + "WSPro.dll")
        self.wrs_pro_5 = ctypes.CDLL(path_to_dll + "WRSystemSPro.dll")
        self.wr_s_pro_5 = ctypes.CDLL(path_to_dll + "WWRSystemSPro.dll")

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

    def store_mfcc_file_data(self, work_type):
        """
        gets all *.mfcc files from resources/mfcc/base folder
        and save all data in self.mfcc dict
        @param work_type: parameter ['learn', 'test'], important for choosing directory with .mfcc files
        """
        file_paths = Utils.get_simple_file_names(path_to_mfcc + "base/" + work_type, ".mfcc")
        words = []
        for i in file_paths:
            word = re.sub("-[0-9]{1,3}\\.mfcc$", "", str(i).lower())
            if not word in self.mfcc[work_type]:
                self.mfcc[work_type][word] = []
            self.mfcc[work_type][word].append(work_type + "/" + i)
            if not word in words:
                words.append(word)
        return words

    def write_mfcc_data_to_file(self, work_type):
        """
        writes self.mfcc into .txt file, WrapperWRSystemSPro will work with this file
        @param work_type: parameter ['learn', 'test'], important for choosing directory with .mfcc files
        """
        f = open(path_to_mfcc + "base/" + work_type + "_base.txt", "w")
        f.write(str(len(self.mfcc[work_type])) + "\n")
        for i in self.mfcc[work_type].keys():
            f.write(str(i).lower() + "\n")
            f.write(str(len(self.mfcc[work_type][i])) + "\n")
            for j in self.mfcc[work_type][i]:
                f.write(j + "\n")
        f.close()

    def wav_to_mfcc(self, base_path, file_paths, i, leading_zeros, waves_path):
        """
        transform one .wav file to .mfcc
        @param base_path: path to folder with .mfcc files for SPro 5.0
        @param file_paths: all wav files for teaching or testing program
        @param i: index of current file
        @param leading_zeros: number of leading zeros in .mfcc filename
        @param waves_path: path to folder with .wav files for SPro 5.0
        @return:
        """
        output_file = re.sub("\\.wav", "-" + str(i + 1).zfill(leading_zeros) + ".mfcc", file_paths[i])
        if os.path.exists(base_path + output_file):
            idx = 2
            while os.path.exists(base_path + output_file):
                output_file = re.sub("\\.wav", "-" + str(i + idx).zfill(leading_zeros) + ".mfcc", file_paths[i])
                idx += 1
        self.s_pro_base_params(waves_path + file_paths[i], base_path + output_file)

    def all_waves_to_mfcc(self, work_type, use_exclude_list=True):
        """
        gets all wav files in dir and transforms each of them into mfcc
        @param work_type: parameter ['learn', 'test'], important for choosing directory with .wav files
        @param use_exclude_list: flag for use or not file with all analyzed wav files early
        """
        base_path = path_to_mfcc + "base/" + work_type + "/"
        waves_path = path_to_mfcc + "waves/" + work_type + "/"

        exclude_file = path_to_mfcc + "waves/excluded_" + work_type + ".txt"
        if use_exclude_list:
            if os.path.exists(exclude_file):
                f = open(exclude_file, "r")
                excluded_lines = f.readlines()
                f.close()
            else:
                excluded_lines = []

        file_paths = Utils.get_simple_file_names(path_to_mfcc + "waves/" + work_type, ".wav")
        leading_zeros = len(str(len(file_paths)))
        excluded = []
        for i in excluded_lines:
            excluded.append(i.replace("\n", ""))
        for i in range(len(file_paths)):
            if use_exclude_list:
                if not file_paths[i] in excluded:
                    excluded.append(file_paths[i])
                    self.wav_to_mfcc(base_path, file_paths, i, leading_zeros, waves_path)
            else:
                self.wav_to_mfcc(base_path, file_paths, i, leading_zeros, waves_path)

        if use_exclude_list:
            f = open(exclude_file, "w")
            f.writelines(excluded)
            f.write("\n")
            f.close()

    def wr_system(self, work_type):
        """
        runs WrapperWRSystemSPro
        @param work_type: ['learn', 'test']
            'learn': for learning system
            'test': for testing system
        base_file: base file name - file with list of mfcc files and words
        system_file: system result file
        wer_file: WER (Word Error Rate) file
        """
        params = [
            "--base " + path_to_mfcc + "base/" + work_type + "_base.txt",
            "--system " + path_to_mfcc + "results/system.bin",
            "--test_results " + path_to_mfcc + "results/wer_" + work_type + "_base.txt"
        ]
        if "learn" == work_type:
            joined_params = "--learn " + ' '.join(params)
        else:
            joined_params = ' '.join(params)
        self.wr_s_pro_5.main(len(joined_params)*2, ctypes.c_wchar_p(joined_params))

    def run(self, work_type, use_exclude_list=True):
        """
        1. converts all exists .wav files to .mfcc
        2. create dict with all needle data (word count, groups with words, files for current word)
        3. write created dict into _base.txt file, which will use in analyzing
        @param work_type: ['learn', 'test']
            'learn': for learning system
            'test': for testing system
        @param use_exclude_list: flag for use or not file with all analyzed wav files early
        """
        self.all_waves_to_mfcc(work_type, use_exclude_list)
        self.store_mfcc_file_data(work_type)
        self.write_mfcc_data_to_file(work_type)
        self.wr_system(work_type)

    def test(self, use_exclude_list=True):
        """
        run program for testing
        @param use_exclude_list: flag for use or not file with all analyzed wav files early
        """
        self.run("test", use_exclude_list)

    def learn(self, use_exclude_list=True):
        """
        run program for teaching
        @param use_exclude_list: flag for use or not file with all analyzed wav files early
        """
        self.run("learn", use_exclude_list)

    @staticmethod
    def get_results():
        """
        analyze wer_test_base.txt file with results of analyzing
        @return: dict with filename of test file (cleared filename) and most possible word from library
        """
        test_file = path_to_mfcc + "results/wer_test_base.txt"
        f = open(test_file, "r")
        data = f.readlines()
        f.close()
        results = {}
        words = data[0].replace("\n", "").split("\t")[1:]
        for i in data[1:len(data)-4]:
            line = str(i).replace("\n", "").split("\t")
            if len(line) > 0:
                results[line[0].replace(": ", "")] = SPro5.get_word(words, list(map(int, line[1:])))
        return results

    @staticmethod
    def get_word(words, coefficients):
        """
        @param words: list with words in library
        @param coefficients: list with coefficients for current test word
        @return: word with max coefficient
        """
        max_val = 0
        word = words[0]
        for i in range(len(words)):
            if coefficients[i] > max_val:
                max_val = coefficients[i]
                word = words[i]
        return word


if "__main__" == __name__:
    s = SPro5(path_to_mfcc_dll)
    s.learn()
    s.test()
    print(SPro5.get_results())