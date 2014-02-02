from tkinter import filedialog, messagebox
import numpy as np
from tkinter.font import Font
from tkinter.ttk import Style, Progressbar
import configparser as cp
from tkinter import *
import webbrowser
from numpy.oldnumeric.linear_algebra import singular_value_decomposition
from Processor import Processor
from WavFile import WavFile

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
        #get program properties

        self.root = root
        self.processor = processor
        self.root.title(self.title)
        self.root.resizable(FALSE, FALSE)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        root.wm_iconbitmap(bitmap=self.cf.get("main_window", "icon_file"))

        self.time = None
        self.progress = None
        self.top_frame = None
        self.main_frame = None
        self.bottom_frame = None

        self.init_ui()
        self.pack()

    def init_ui(self):
        self.style = Style()
        self.style.theme_use('default')

        self.init_menu()
        self.init_top_frame()
        self.init_main_frame()
        self.init_bottom_frame()

    def init_menu(self):
        menu_bar = Menu(self.root)
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def about(self):
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

    def init_main_frame(self):
        self.main_frame = Frame(self, relief=SUNKEN, height=300, width=500)
        Button(self.main_frame, text="Teach Program", command=self.make_teach_main_frame, width=15).pack()
        self.main_frame.pack(side=TOP)

    def init_top_frame(self):
        self.top_frame = Frame(self, relief=RIDGE, height=50, bg="white", borderwidth=1)
        Label(self.top_frame, text="Welcome to " + self.title, bg="white",
              font=Font(family=self.font_family, size=10, weight="bold")).pack(side=TOP, anchor=W, pady=5, padx=5)

        Label(self.top_frame, text="You can teach program or use default data", bg="white",
              font=Font(family=self.font_family, size=8)).pack(side=TOP, anchor=W, padx=10)

        self.top_frame.pack(side=TOP, fill=BOTH)

    def init_bottom_frame(self):
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
        # answer = messagebox.askyesno(parent=self, message='Are you sure you want to close program?',
        #                              icon='question', title='Close')
        # if answer:
        self.root.destroy()

    def make_teach_main_frame(self):
        for child in self.main_frame.winfo_children():
            child.destroy()

        self.time = IntVar(self.main_frame)
        Label(self.main_frame, text="Select time of you future recording:").pack(side=TOP, anchor=NW)

        frame_left = Frame(self.main_frame)
        for i in range(self.min_audio_time, self.max_audio_time+1):
            Radiobutton(frame_left, text=str(i) + " sec", indicatoron=0, variable=self.time, value=i,
                        width=20).pack(side=TOP, anchor=NW)
        frame_left.pack(side=LEFT, anchor=NW)

        right_frame = Frame(self.main_frame)
        self.progress = Progressbar(right_frame, orient=HORIZONTAL, length=200, mode='determinate')
        self.progress.pack(side=TOP, anchor=NE)
        Button(right_frame, text="Record audio", command=self.record, width=15).pack(side=TOP, anchor=NE)
        right_frame.pack(side=LEFT, anchor=NE)

        self.main_frame.pack()

    def record(self):
        if self.time.get() == 0:
            self.time.set(self.default_audio_time)
        file_name = filedialog.asksaveasfilename(filetypes=[("Wave audio files", "*.wav *.wave")],
                                                 defaultextension=".wav", initialdir="./audio_files/records")
        if len(file_name) == 0:
            messagebox.showwarning("Warning", "You must save new file!")
        else:
            self.progress.start()
            self.processor.recorder.record_audio_to_file(time=self.time.get(), file_name=file_name)
            self.progress.stop()


def main():
    cf = cp.ConfigParser()
    cf.read("properties/properties.cfg")
    processor = Processor("examples", np.fft.fft,
                          lambda: WavFile("waves/silenceSmall.wav").get_one_channel_data())
    root = Tk()
    app = Application(root, cf, processor)
    root.mainloop()


if __name__ == '__main__':
    main()