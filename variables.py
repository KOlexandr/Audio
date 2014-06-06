import os
from configparser import ConfigParser

__author__ = 'Olexandr'

path_to_project = str(os.path.dirname(__file__)).replace("\\", "/")

#cf: configurations parser, for get all parameters saved in configuration file
cf = ConfigParser()
cf.read(path_to_project + "/properties/properties.cfg")

#Naive Bayes Classifier
path_to_speech = str(path_to_project + cf.get("nbc", "path_to_speech"))
path_to_non_speech = str(path_to_project + cf.get("nbc", "path_to_non_speech"))

#Resources
path_to_mfcc = str(path_to_project + cf.get("resources", "path_to_mfcc"))
path_to_test = str(path_to_project + cf.get("resources", "path_to_test"))
path_to_flacs = str(path_to_project + cf.get("resources", "path_to_flacs"))
path_to_records = str(path_to_project + cf.get("resources", "path_to_records"))
path_to_examples = str(path_to_project + cf.get("resources", "path_to_examples"))
path_to_wav2mfcc = str(path_to_project + cf.get("resources", "path_to_wav2mfcc"))
path_to_silence = str(path_to_project + cf.get("resources", "path_to_small_silence"))
path_to_vad_results = str(path_to_project + cf.get("resources", "path_to_vad_results"))

#SQLite DataBase
path_to_database = str(path_to_project + "/resources/speech.db")

#MFCC
use_exe = bool(int(cf.get("mfcc", "use_exe")))

#Plots
show_plots = bool(int(cf.get("plots", "show_plots")))

#FIR
use_filter = bool(int(cf.get("fir", "use_filter")))