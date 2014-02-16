from tkinter import filedialog, messagebox
from tkinter.font import Font
from tkinter.ttk import Style
import configparser as cp
from tkinter import *
import numpy as np
import webbrowser

from Processor import Processor
from WavFile import WavFile
from vad import VAD

__author__ = 'Olexandr'


class Application(Frame):
    def __init__(self, root, cf, processor):
        Frame.__init__(self, root)
        self.cf = cf

        #get general properties
        self.title = self.cf.get("general", "title")
        self.author = self.cf.get("general", "author")
        self.link_color = self.cf.get("general", "link_color")
        self.link_cursor = self.cf.get("general", "link_cursor")
        self.font_family = self.cf.get("general", "font_family")
        self.author_email = self.cf.get("general", "author_email")
        self.copyright_year = self.cf.get("general", "copyright_year")
        self.author_google_plus = self.cf.get("general", "author_google_plus")
        self.license_agree_link = self.cf.get("general", "license_agree_link")
        #get general properties

        #get program properties
        self.min_audio_time = int(self.cf.get("program", "min_audio_time"))
        self.max_audio_time = int(self.cf.get("program", "max_audio_time"))
        self.default_audio_time = int(self.cf.get("program", "default_audio_time"))
        self.min_test_audio_time = int(self.cf.get("program", "min_test_audio_time"))
        self.max_test_audio_time = int(self.cf.get("program", "max_test_audio_time"))
        self.default_test_audio_time = int(self.cf.get("program", "default_test_audio_time"))
        #get program properties

        self.root = root
        self.processor = processor
        self.root.title(self.title)
        self.root.resizable(FALSE, FALSE)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        root.wm_iconbitmap(bitmap=self.cf.get("main_window", "icon_file"))

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
        ok_hover_bg = self.cf.get(window, "ok_hover_bg")
        ok_default_bg = self.cf.get(window, "ok_default_bg")
        font = Font(family=self.font_family, size=10)

        #main frame
        top = Toplevel(self)
        top.resizable(FALSE, FALSE)
        top.title("About " + self.title)
        top.wm_iconbitmap(bitmap=self.cf.get(window, "icon_file"))

        #info frame in main frame
        frame = Frame(top, relief=SUNKEN, bg="white", borderwidth=1)

        Label(frame, text="This program was create for course work.", bg="white", font=font).pack(padx=5, pady=5)
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

    def make_main_frame(self):
        """
        makes simple GUI of main window with 2 buttons record example file (Teach Program)
        and record test audio and analyze it (Record and Analyze Sound)
        """
        self.clear_frame(self.main_frame)
        Button(self.main_frame, text="Teach Program",
               command=lambda: self.make_record_frame(self.min_audio_time, self.max_audio_time,
                                                      self.record_example_audio), width=15).pack()
        Button(self.main_frame, text="Record and Analyze Sound",
               command=lambda: self.make_record_frame(self.min_test_audio_time, self.max_test_audio_time,
                                                      self.record_test_audio),
               width=30).pack()
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

    def record_example_audio(self, time):
        """
        records short audio file (file example with some word)
        and adds it to library
        @param time: length of test file
        """
        if time.get() == 0:
            time.set(self.default_audio_time)
        file_name = filedialog.asksaveasfilename(filetypes=[("Wave audio files", "*.wav *.wave")],
                                                 defaultextension=".wav",
                                                 initialdir=self.cf.get("program", "base_save_folder"))
        if len(file_name) == 0:
            messagebox.showwarning("Warning", "You must input name of new file, and save it!")
        else:
            wav = self.processor.recorder.record_audio_to_file_and_get_wav(time=time.get(), file_name=file_name)
            self.processor.lib.create_and_add_item_from_wave(wav)
            messagebox.showinfo("File Saved", "Audio recorded, saved into file and added to library!")

    def record_test_audio(self, time):
        """
        records audio from microphone and uses this audio for analyzing
        @param time: length of test file
        """
        if time.get() == 0:
            time.set(self.default_test_audio_time)
        wav = self.processor.recorder.record_and_get_wav(time.get())
        samples, word_count, max_len = self.processor.find_word_in_test_file(wav.get_one_channel_data())
        result_str = "All words in file = " + str(word_count) + "\n"
        print("All words in file = " + str(word_count))
        for j in samples:
            word, coefficient = self.processor.lib.find_max_corrcoef_and_word(j, max_len)
            if coefficient > 0.3:
                result_str += word + " - " + str(coefficient) + "\n"
                print(word + " - " + str(coefficient))
        messagebox.showinfo("Result", result_str)


def main():
    # cf = cp.ConfigParser()
    # cf.read("properties/properties.cfg")
    # processor = Processor(cf.get("program", "base_examples_folder"), np.fft.fft,
    #                       lambda: WavFile(cf.get("program", "path_to_small_silence_wav")).get_one_channel_data())
    # root = Tk()
    # app = Application(root, cf, processor)
    # root.mainloop()
    wav = WavFile("resources/audio_files/files/examples/seven_.wav")
    VAD.vad(wav)



if __name__ == '__main__':
    main()