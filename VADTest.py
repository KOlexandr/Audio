from algorithms.vad import VAD
from algorithms.vad.VADUtils import find_words_for_one_param
from beans.WavFile import WavFile
from handlers.Plotter import Plotter

__author__ = 'Olexandr'


def plot_result(energy, mdf, min_e, min_mdf, min_sfm, min_zcr, sfm, wav, word_ends_energy, word_ends_mdf, word_ends_sfm,
                word_ends_zcr, word_starts_energy, word_starts_mdf, word_starts_sfm, word_starts_zcr, zcr,
                items_per_frame):
    plot = Plotter()
    plot.add_sub_plot_data("samples", wav.get_one_channel_data())
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_starts_energy)), "x", color="red", lw=3)
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_ends_energy)), "x", color="red", lw=3)
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_starts_zcr)), "x", color="green", lw=3)
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_ends_zcr)), "x", color="green", lw=3)
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_starts_mdf)), "x", color="black", lw=3)
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_ends_mdf)), "x", color="black", lw=3)
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_starts_sfm)), "x", color="yellow", lw=3)
    plot.add_line_at("samples", list(map(lambda x: x * items_per_frame, word_ends_sfm)), "x", color="yellow", lw=3)
    plot.add_sub_plot_data("energy", energy)
    plot.add_line_at("energy", min_e, "y", color="red")
    plot.add_sub_plot_data("zcr", zcr)
    plot.add_line_at("zcr", min_zcr, "y", color="red")
    plot.add_sub_plot_data("mdf", mdf)
    plot.add_line_at("mdf", min_mdf, "y", color="red")
    plot.add_sub_plot_data("sfm", sfm)
    plot.add_line_at("sfm", min_sfm, "y", color="red")
    plot.sub_plot_all_horizontal()


def main(file_name, min_frames_voice, min_frames_noise, bad_frames_count):
    wav = WavFile(file_name)
    parameters = VAD.vad(wav)
    items_per_frame = parameters["items_per_frame"]
    energy = parameters["energy"]
    mdf = parameters["mdf"]
    zcr = parameters["zcr"]
    sfm = parameters["sfm"]
    if bad_frames_count == 0:
        min_e = min(energy) + 1
        min_zcr = min(mdf) + 1
        #320 near 0.01*32768
        min_mdf = min(zcr) + 320
        min_sfm = min(sfm) + 1
    else:
        min_e = max(energy[0:bad_frames_count])
        min_zcr = max(zcr[0:bad_frames_count])
        min_mdf = max(mdf[0:bad_frames_count])
        min_sfm = max(sfm[0:bad_frames_count])

    word_starts_energy, word_ends_energy = find_words_for_one_param(energy, min_e, min_frames_voice, min_frames_noise)
    word_starts_zcr, word_ends_zcr = find_words_for_one_param(zcr, min_zcr, min_frames_voice, min_frames_noise)
    word_starts_mdf, word_ends_mdf = find_words_for_one_param(mdf, min_mdf, min_frames_voice, min_frames_noise)
    word_starts_sfm, word_ends_sfm = find_words_for_one_param(sfm, min_sfm, min_frames_voice, min_frames_noise)

    plot_result(energy, mdf, min_e, min_mdf, min_sfm, min_zcr, sfm, wav, word_ends_energy, word_ends_mdf, word_ends_sfm,
                word_ends_zcr, word_starts_energy, word_starts_mdf, word_starts_sfm, word_starts_zcr, zcr,
                items_per_frame)


if "__main__" == __name__:
    main("resources/audio_files/waves/12345678910.wav", 3, 3, 0)