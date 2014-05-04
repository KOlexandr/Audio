import ctypes
import os

__author__ = 'Olexandr'

path_to_dll = os.path.dirname(__file__) + "/SProWrapper.dll"


class SPro5:
    """
    wrapper for SPro 5.0 c program
    use DLL for transform wav file to mfcc
    """

    def main(self):
        dll = ctypes.CDLL(path_to_dll)
        data = "--format=wave --sample-rate=16000 --mel --freq-min=0 --freq-max=8000 --fft-length=256 --length=16.0" + \
               " --shift=10.0 --num-ceps=13 test.wav test.mfcc"

        dll.main(len(data) * 2, ctypes.c_wchar_p(data))


if "__main__" == __name__:
    s = SPro5()
    s.main()