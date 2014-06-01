from variables import path_to_flacs, path_to_test
from urllib.request import Request, urlopen
import glob
import os
import re

__author__ = 'Olexandr'


class WavFLAC:
    def __init__(self, lang_code='en-US'):
        self.lang_code = lang_code
        self.flac_path = (os.path.dirname(__file__) + "/flac").replace("\\", "/")
        self.google_speech_url = "https://www.google.com/speech-api/v1/recognize"

    def wav2flac(self, path_to_wav, path_to_flac):
        """
        convert one wav file to flac or list of vaw files to flac
        @param path_to_wav: path to wav file or directory with wav files
        @param path_to_flac: path to new flac file or directory with new flac files
        @return: path or list of paths to new flac files
        """
        files = {}
        if path_to_wav.endswith('.wav') and path_to_flac.endswith('.flac'):
            files[path_to_wav] = path_to_flac
        elif type(path_to_wav) == str and os.path.isdir(path_to_wav) and type(path_to_flac) == str and os.path.isdir(
                path_to_flac):
            wav_files = list(map(lambda x: x.replace("\\", "/"), glob.glob(os.path.join(path_to_wav, '*.wav'))))
            for i in wav_files:
                re_sub = re.sub("\\.wav$", ".flac", str(i).lower())
                files[i] = path_to_flac + "/" + re_sub[re_sub.rfind("/") + 1:]
        else:
            return None
        if len(files) == 0:
            return None
        else:
            for wav_file in files.keys():
                os.system(self.flac_path + " --totally-silent -e -f " + wav_file + " -o " + files[wav_file])
            if len(files) == 1:
                return list(files.values())[0]
            else:
                return list(files.values())

    def flac2wav(self, path_to_flac, path_to_wav):
        """
        convert one flac file to wav or list of flac files to wav
        @param path_to_flac: path to flac file or directory with flac files
        @param path_to_wav: path to new wav file or directory with new wav files
        @return: path or list of paths to new wav files
        """
        files = {}
        if path_to_flac.endswith('.flac') and path_to_wav.endswith('.wav'):
            files[path_to_flac] = path_to_wav
        elif type(path_to_flac) == str and os.path.isdir(path_to_flac) and type(path_to_wav) == str and os.path.isdir(
                path_to_wav):
            flac_files = list(map(lambda x: x.replace("\\", "/"), glob.glob(os.path.join(path_to_wav, '*.flac'))))
            for i in flac_files:
                re_sub = re.sub("\\.flac$", ".wav", str(i).lower())
                files[i] = path_to_flac + "/" + re_sub[re_sub.rfind("/") + 1:]
        else:
            return None
        if len(files) == 0:
            return None
        else:
            for flac_file in files.keys():
                os.system(self.flac_path + " --totally-silent -d -f " + flac_file + " -o " + files[flac_file])
            if len(files) == 1:
                return list(files.values())[0]
            else:
                return list(files.values())

    @staticmethod
    def generate_file(filename):
        re_sub = re.sub("\\.wav$", ".flac", str(filename).lower())
        return "/" + re_sub[re_sub.rfind("/") + 1:]

    def stt_google_wav(self, audio_file):
        """ Sends audio file (audio_fname) to Google's text to speech
            service and returns service's response. We need a FLAC
            converter if audio is not FLAC. """

        audio_file = audio_file.replace("\\", "/")
        #Convert to flac first
        if str(audio_file).endswith(".wav"):
            filename = self.wav2flac(audio_file, path_to_flacs + self.generate_file(audio_file))
            is_flac = True
        else:
            filename = audio_file
            is_flac = False

        f = open(filename, 'rb')
        flac_cont = f.read()
        f.close()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" +
                          " Chrome/29.0.1547.57 Safari/537.36",
            'Content-type': 'audio/x-flac; rate=44100'
        }

        req = Request(self.google_speech_url, data=flac_cont, headers=headers)
        p = urlopen(req)
        response = p.read()
        res = eval(response)['hypotheses']

        if is_flac:
            # Remove temp file
            os.remove(filename)

        return res

if "__main__" == __name__:
    converter = WavFLAC()
    file = converter.wav2flac(path_to_test + '12345678910.wav', path_to_flacs + '12345678910.flac')