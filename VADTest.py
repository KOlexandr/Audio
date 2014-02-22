from algorithms.vad import VAD
from algorithms.vad.VADUtils import find_words_for_one_param
from beans.WavFile import WavFile
from handlers.Plotter import Plotter

__author__ = 'Olexandr'


def plot_result(wav, word_results, params, min_params, colors, items):
    plot = Plotter()
    plot.add_sub_plot_data("samples", wav.get_one_channel_data())
    for i in word_results.keys():
        plot.add_line_at("samples", list(map(lambda x: x * items, word_results[i]["starts"])), "x", colors[i], lw=3)
        plot.add_line_at("samples", list(map(lambda x: x * items, word_results[i]["ends"])), "x", colors[i], lw=3)

    for i in word_results.keys():
        plot.add_sub_plot_data(i, params[i])
        plot.add_line_at(i, min_params[i], "y", color="red")
    plot.sub_plot_all_horizontal()


def main(file_name, min_frames_voice, min_frames_noise, bad_frames_count):
    keys, shifts = ["energy", "mdf", "zcr", "sfm"], {"energy": 1, "mdf": 320, "zcr": 1, "sfm": 1}
    colors = {"energy": "red", "mdf": "green", "zcr": "black", "sfm": "yellow"}
    wav = WavFile(file_name)
    params = VAD.vad(wav)
    min_params = {}
    if bad_frames_count == 0:
        for i in keys:
            min_params[i] = min(params[i]) + shifts[i]
    else:
        for i in keys:
            min_params[i] = max(params[i][0:bad_frames_count])
    word_results = {}
    for i in keys:
        if word_results.get(i) is None:
            word_results[i] = {}
        starts, ends = find_words_for_one_param(params[i], min_params[i], min_frames_voice, min_frames_noise)
        word_results[i]["starts"], word_results[i]["ends"] = starts, ends

    plot_result(wav, word_results, params, min_params, colors, params["items_per_frame"])


if "__main__" == __name__:
    main("resources/audio_files/waves/12345678910.wav", 3, 3, 0)