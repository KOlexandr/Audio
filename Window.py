from variables import path_to_records, path_to_silence, cf, path_to_mfcc, path_to_test, path_to_examples, show_plots
from algorithms.fva import FFTVoiceAnalyzer
from algorithms.nbc import NBC
from tkinter import filedialog, messagebox
from handlers.Plotter import Plotter
from algorithms.wav2mfcc import SPro5
from beans.WavFile import WavFile
from algorithms.vad import test
from tkinter.font import Font
from tkinter.ttk import Style
from tkinter import *
import numpy as np
import webbrowser

__author__ = 'Olexandr'


class Application(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

        #========================================================================
        # Fast Fourier Transform
        self.processor = FFTVoiceAnalyzer(path_to_examples, np.fft.fft, WavFile(path_to_silence))
        # Fast Fourier Transform
        #========================================================================

        #========================================================================
        # Naive Bayes Classifier
        self.nbc = NBC()
        self.nbc.initialize()
        # Naive Bayes Classifier
        #========================================================================

        #========================================================================
        # SPro 5 (MFCC classifierd)
        self.s = SPro5()
        self.s.learn()
        # SPro 5 (MFCC classifierd)
        #========================================================================

        #get general properties
        self.title = cf.get("general", "title")
        self.author = cf.get("general", "author")
        self.link_color = cf.get("general", "link_color")
        self.link_cursor = cf.get("general", "link_cursor")
        self.font_family = cf.get("general", "font_family")
        self.author_email = cf.get("general", "author_email")
        self.copyright_year = cf.get("general", "copyright_year")
        self.author_google_plus = cf.get("general", "author_google_plus")
        self.license_agree_link = cf.get("general", "license_agree_link")
        #get general properties

        #get program properties
        self.min_audio_time = int(cf.get("program", "min_audio_time"))
        self.max_audio_time = int(cf.get("program", "max_audio_time"))
        self.default_audio_time = int(cf.get("program", "default_audio_time"))
        self.min_test_audio_time = int(cf.get("program", "min_test_audio_time"))
        self.max_test_audio_time = int(cf.get("program", "max_test_audio_time"))
        self.default_test_audio_time = int(cf.get("program", "default_test_audio_time"))
        #get program properties

        self.root = root
        self.root.title(self.title)
        self.root.resizable(FALSE, FALSE)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        root.wm_iconbitmap(bitmap=cf.get("main_window", "icon_file"))

        self.top_frame = None
        self.main_frame = None
        self.bottom_frame = None

        self.init_ui()
        self.pack()

    def init_ui(self):
        """
        initialize all GUI
        """
        self.style = Style()
        self.style.theme_use('default')

        self.init_menu()
        self.init_top_frame()

        self.main_frame = Frame(self, relief=SUNKEN)
        self.make_main_frame()

        self.init_bottom_frame()

    def init_menu(self):
        """
        initialize menu (now menu has only 'About' element)
        """
        menu_bar = Menu(self.root)
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def about(self):
        """
        makes simple GUI of About window
        """
        window = "about_window"
        ok_hover_bg = cf.get(window, "ok_hover_bg")
        ok_default_bg = cf.get(window, "ok_default_bg")
        font = Font(family=self.font_family, size=10)

        #main frame
        top = Toplevel(self)
        top.resizable(FALSE, FALSE)
        top.title("About " + self.title)
        top.wm_iconbitmap(bitmap=cf.get(window, "icon_file"))

        #info frame in main frame
        frame = Frame(top, relief=SUNKEN, bg="white", borderwidth=1)

        Label(frame, text="Voice Analyzer. Simple program for speech recognition, created for qualification work",
              bg="white", font=font).pack(padx=5, pady=5)
        Label(frame, text="Copyright " + self.copyright_year + ". GNU License. All rights reserved.",
              bg="white", font=font).pack(padx=5, pady=5)

        #author
        link_info = Message(frame, text="Author: " + self.author, bg="white", font=font, width=250)
        link_info.pack(side=LEFT, anchor=E, padx=5, pady=5)

        #link to author page (somewhere)
        link = Label(frame, text="Google Plus", bg="white", fg=self.link_color, font=font, cursor=self.link_cursor)
        link.bind("<Button-1>", lambda x: webbrowser.open_new_tab(self.author_google_plus))
        link.pack(side=LEFT, anchor=S, pady=5)
        frame.pack()

        #OK button in main frame
        button = Button(top, text="OK", command=top.destroy, width=10, bg=ok_default_bg, borderwidth=1)
        button.bind("<Enter>", lambda event, h=button: self.change_bg(h, ok_hover_bg))
        button.bind("<Leave>", lambda event, h=button: self.change_bg(h, ok_default_bg))
        button.pack(side=RIGHT, anchor=S, padx=5, pady=5)

    @staticmethod
    def change_bg(item, new_bg):
        item.configure(bg=new_bg)
        item.pack()

    @staticmethod
    def clear_frame(frame):
        for child in frame.winfo_children():
            child.destroy()

    #==================================================================================================================
    #========================================================================
    # Record Audio
    def record_audio(self, time, path=path_to_records):
        """
        record audio data to file
        @param time: length of file in sec
        """
        file_name = filedialog.asksaveasfilename(filetypes=[("Wave audio files", "*.wav *.wave")],
                                                 defaultextension=".wav", initialdir=path)
        if len(file_name) == 0:
            messagebox.showwarning("Warning", "You must input name of new file, and save it!")
            return None
        else:
            wav = self.processor.recorder.record_audio_to_file_and_get_wav(time=time, file_name=file_name)
            messagebox.showinfo("File Saved", "Audio has recorded.")
            return wav

    def record_test_audio(self, time):
        """
        records audio from microphone and uses this audio for analyzing
        @param time: length of test file
        """
        if time.get() == 0:
            time.set(self.default_test_audio_time)
        return self.processor.recorder.record_and_get_wav(time.get())
    # Record Audio
    #========================================================================

    #========================================================================
    # Fast Fourier Transform Voice Analyzer
    def fft_analyzer_record_to_lib(self, time):
        """
        records short audio file (file example with some word)
        and adds it to library
        @param time: length of test file
        """
        if time.get() == 0:
            time.set(self.default_audio_time)
        wav = self.record_audio(time.get())
        self.processor.lib.create_and_add_item_from_wave(wav)

    def fft_analyzer_record(self, time):
        if time.get() == 0:
            time.set(self.default_audio_time)

        wav = self.record_test_audio(time)
        if not wav is None:
            result_str = FFTVoiceAnalyzer.analyze(wav, self.processor)
            messagebox.showinfo("Result", result_str)
            if show_plots:
                plot = Plotter()
                plot.add_sub_plot_data("Digitized Recorded Audio", wav.get_one_channel_data(), x_label="Samples",
                                       y_label="Amplitude")
                plot.sub_plot_all_horizontal()

    def fft_analyzer_select(self, path=path_to_test):
        askopenfile = filedialog.askopenfile(filetypes=[("Wave audio files", "*.wav *.wave")], defaultextension=".wav",
                                             initialdir=path)
        if not askopenfile is None:
            wav = WavFile(askopenfile.name)
            result_str = FFTVoiceAnalyzer.analyze(wav, self.processor)
            messagebox.showinfo("Result", result_str)
            if show_plots:
                plot = Plotter()
                plot.add_sub_plot_data("Digitized Recorded Audio", wav.get_one_channel_data(), x_label="Samples",
                                       y_label="Amplitude")
                plot.sub_plot_all_horizontal()
        else:
            messagebox.showwarning("Warning", "You should select one file. Please, try again")
    # Fast Fourier Transform Voice Analyzer
    #========================================================================

    #========================================================================
    # Naive Bayes Classifier
    def nbc_add_file_select(self, clazz, path=path_to_records):
        askopenfile = filedialog.askopenfile(filetypes=[("Wave audio files", "*.wav *.wave")], defaultextension=".wav",
                                             initialdir=path)
        if not askopenfile is None:
            self.nbc.add_one_audio_file(clazz, path_to_file=askopenfile.name)
            self.nbc.teach_classifier()

    def nbc_classify_file_select(self, path=path_to_test):
        askopenfile = filedialog.askopenfile(filetypes=[("Wave audio files", "*.wav *.wave")], defaultextension=".wav",
                                             initialdir=path)
        if not askopenfile is None:
            print("Teaching NBC classifier with added examples")
            self.nbc.teach_classifier()
            print("Teaching NBC classifier finished")
            classes = self.nbc.get_classes(self.nbc.classify(WavFile(askopenfile.name)))
            mess = ""
            for i in classes.keys():
                for j in classes[i].keys():
                    mess += str(i) + ": " + str(j) + "\n"
            messagebox.showinfo("Classification results", mess)
        else:
            messagebox.showwarning("Warning", "You should select one file. Please, try again")
    # Naive Bayes Classifier
    #========================================================================

    #========================================================================
    # Voice Activity Detection
    def show_test_vad_open(self, path=path_to_test):
        askopenfile = filedialog.askopenfile(filetypes=[("Wave audio files", "*.wav *.wave")], defaultextension=".wav",
                                             initialdir=path)
        if not askopenfile is None:
            test(WavFile(askopenfile.name), self.nbc)
        else:
            messagebox.showwarning("Warning", "You should select one file. Please, try again")

    def show_test_vad_record(self, time):
        wav = self.record_test_audio(time)
        if not wav is None:
            test(wav, self.nbc)
            if show_plots:
                plot = Plotter()
                plot.add_sub_plot_data("Digitized Recorded Audio", wav.get_one_channel_data(), x_label="Samples",
                                       y_label="Amplitude")
                plot.sub_plot_all_horizontal()
    # Voice Activity Detection
    #========================================================================

    def add_mfcc_file(self, file_type, path=path_to_mfcc):
        if not self.record_audio(5, path=path + "waves/" + file_type) is None:
            self.s.learn()

    def show_test_mfcc(self):
        self.s.test()
        str_res = SPro5.get_results()
        messagebox.showinfo("Results MFCC", str_res)

    #==================================================================================================================

    def make_main_frame(self):
        """
        makes simple GUI of main window with 2 buttons record example file (Teach Program)
        and record test audio and analyze it (Record and Analyze Sound)
        """
        self.clear_frame(self.main_frame)

        #========================================================================
        # Record Audio
        Label(self.main_frame, text="Record Audio File",
              font=Font(family=self.font_family, size=10, weight="bold")).pack(side=TOP, pady=5, padx=5)
        Button(self.main_frame, text="Record",
               command=lambda: self.make_record_frame(self.min_audio_time, self.max_audio_time,
                                                      self.record_audio), width=15).pack()
        # Record Audio
        #========================================================================

        #========================================================================
        # Fast Fourier Transform Voice Analyzer
        Label(self.main_frame, text="FFT Voice Analyzer",
              font=Font(family=self.font_family, size=10, weight="bold")).pack(side=TOP, pady=5, padx=5)
        Button(self.main_frame, text="Record and Teach Program",
               command=lambda: self.make_record_frame(self.min_audio_time, self.max_audio_time,
                                                      self.fft_analyzer_record_to_lib), width=30).pack()
        Button(self.main_frame, text="Record and Analyze Sound",
               command=lambda: self.make_record_frame(self.min_test_audio_time, self.max_test_audio_time,
                                                      self.fft_analyzer_record),
               width=30).pack()
        Button(self.main_frame, text="Choose and Analyze Sound",
               command=lambda: self.fft_analyzer_select(), width=30).pack()
        # Fast Fourier Transform Voice Analyzer
        #========================================================================

        #========================================================================
        # Naive Bayes Classifier
        Label(self.main_frame, text="Naive Bayes Classifier",
              font=Font(family=self.font_family, size=10, weight="bold")).pack(side=TOP, pady=5, padx=5)
        Button(self.main_frame, text="Add Speech File for NBC", command=lambda: self.nbc_add_file_select("speech"),
               width=30).pack()
        Button(self.main_frame, text="Add Non Speech File for NBC",
               command=lambda: self.nbc_add_file_select("non_speech"),
               width=30).pack()
        Button(self.main_frame, text="Choose and Classify File", command=lambda: self.nbc_classify_file_select(),
               width=30).pack()
        # Naive Bayes Classifier
        #========================================================================

        #========================================================================
        # Voice Activity Detection
        Label(self.main_frame, text="Voice Activity Detection",
              font=Font(family=self.font_family, size=10, weight="bold")).pack(side=TOP, pady=5, padx=5)
        Button(self.main_frame, text="Record and Analyze",
               command=lambda: self.make_record_frame(self.min_audio_time, self.max_audio_time,
                                                      self.show_test_vad_record), width=30).pack()
        Button(self.main_frame, text="Choose and Analyze", command=lambda: self.show_test_vad_open(), width=30).pack()
        # Voice Activity Detection
        #========================================================================

        #========================================================================
        # SPro 5 (MFCC classifierd)
        Label(self.main_frame, text="MFCC",
              font=Font(family=self.font_family, size=10, weight="bold")).pack(side=TOP, pady=5, padx=5)
        Button(self.main_frame, text="Test", command=lambda: self.show_test_mfcc(), width=30).pack()
        Button(self.main_frame, text="Record Test File", command=lambda: self.add_mfcc_file("test"), width=30).pack()
        Button(self.main_frame, text="Record Learn File", command=lambda: self.add_mfcc_file("learn"), width=30).pack()
        # SPro 5 (MFCC classifierd)
        #========================================================================

        self.main_frame.pack(side=TOP)

    def init_top_frame(self):
        """
        initialize head of main window
        """
        self.top_frame = Frame(self, relief=RIDGE, height=50, bg="white", borderwidth=1)
        Label(self.top_frame, text="Welcome to " + self.title, bg="white",
              font=Font(family=self.font_family, size=10, weight="bold")).pack(side=TOP, anchor=W, pady=5, padx=5)

        Label(self.top_frame, text="You can teach program or use default data", bg="white",
              font=Font(family=self.font_family, size=8)).pack(side=TOP, anchor=W, padx=10)

        self.top_frame.pack(side=TOP, fill=BOTH)

    def init_bottom_frame(self):
        """
        initialize footer of main window
        """
        self.bottom_frame = Frame(self, relief=GROOVE, height=50, borderwidth=1)
        Button(self.bottom_frame, text="Cancel", command=self.close, width=10).pack(side=RIGHT, padx=5, pady=5)

        font = Font(family=self.font_family, size=8)
        link = Label(self.bottom_frame, text="License Agreement:", fg=self.link_color, font=font,
                     cursor=self.link_cursor)
        link.bind("<Button-1>", lambda x: webbrowser.open_new_tab(self.license_agree_link))
        link.pack(side=LEFT, pady=5)
        text = Label(self.bottom_frame, text="By continuing, you agree to the term of the license agreement.",
                     font=font)
        text.pack(side=LEFT, pady=5)

        self.bottom_frame.pack(side=BOTTOM, fill=BOTH)

    def close(self):
        """
        close program dialog
        """
        answer = messagebox.askyesno(parent=self, message='Are you sure you want to close program?',
                                     icon='question', title='Close')
        if answer:
            self.root.destroy()

    def make_record_frame(self, min_time, max_time, record_function):
        """
        make simple GUI of record window
        @param min_time: minimum length of audio which will record
        @param max_time: maximum length of audio which will record
        @param record_function: command for record button (now: record example audio or test audio)
        """
        self.clear_frame(self.main_frame)
        time = IntVar(self.main_frame)
        Label(self.main_frame, text="Time:").pack(side=LEFT)
        Spinbox(self.main_frame, from_=min_time, to=max_time, textvariable=time).pack(side=LEFT)
        Button(self.main_frame, text="Record audio", command=lambda: record_function(time), width=20).pack(side=LEFT)
        Button(self.main_frame, text="Back", command=self.make_main_frame, width=20).pack(side=LEFT)
        self.main_frame.pack()


def main():
    root = Tk()
    Application(root)
    root.mainloop()


if __name__ == '__main__':
    main()