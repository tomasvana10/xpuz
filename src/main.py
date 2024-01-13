import tkinter as tk 
import tkinter.messagebox
import gettext
import locale
import os
from pathlib import Path
from PIL import Image
from configparser import ConfigParser

import customtkinter as ctk 
from babel import Locale

import cword_gen as cwg


class Paths:
    CONFIG_PATH = Path(__file__).resolve().parents[0] / "config.ini"
    LOCALES_PATH = Path(__file__).resolve().parents[1] / "locales"
    CWORD_IMG_PATH = Path(__file__).resolve().parents[1] / "assets/images/cword_showcase.png"


class Colour:
    class Light:
        FRAME_L = "#B0BEC5"
        FRAME_R = "#CFD8DC"

    class Dark:
        FRAME_L = "#263238"
        FRAME_R = "#37474F"


class Style:
    TITLE_FONT = {"size": 30, "weight": "bold", "slant": "roman"}
    SUBHEADING_FONT = {"size": 23, "weight": "normal", "slant": "italic"}
    LABEL_FONT = {"size": 14, "weight": "bold", "slant": "roman"}


class Home(ctk.CTk):
    def __init__(self, lang_info, locale_):
        super().__init__()
        self.locale_ = locale_ 
        AppHelper._update_config("m", "language", locale_.language)
        self.lang_db, self.lang_options = lang_info
        self.title("Crossword Puzzle - Home")
        self.geometry("800x600")
        ctk.set_appearance_mode(cfg.get("m", "appearance"))
        ctk.set_default_color_theme(cfg.get("m", "theme"))
        ctk.set_widget_scaling(float(cfg.get("m", "scale")))
        
        self.protocol("WM_DELETE_WINDOW", self._exit_handler)
        
        self._make_frames()
        self._make_content()

    def _make_frames(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.settings_frame = ctk.CTkFrame(self.main_frame, 
                                           fg_color=(Colour.Light.FRAME_R, Colour.Dark.FRAME_R),
                                           corner_radius=0)
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        
        self.cword_opts_frame = ctk.CTkFrame(self.main_frame, 
                                             fg_color=(Colour.Light.FRAME_L, Colour.Dark.FRAME_L), 
                                             corner_radius=0)
        self.cword_opts_frame.grid(row=0, column=0, sticky="nsew")

    def _make_content(self):
        title = ctk.CTkLabel(self.cword_opts_frame, text="Crossword Puzzle", font=ctk.CTkFont(
                             size=Style.TITLE_FONT["size"],
                             weight=Style.TITLE_FONT["weight"]))
        title.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        cword_img = ctk.CTkLabel(self.cword_opts_frame, text="", 
                                 image=ctk.CTkImage(Image.open(Paths.CWORD_IMG_PATH), 
                                                    size=(453, 154)))
        cword_img.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        settings_label = ctk.CTkLabel(self.settings_frame, text="Global Settings", 
                                      font=ctk.CTkFont(size=Style.SUBHEADING_FONT["size"],
                                                       slant=Style.SUBHEADING_FONT["slant"]))
        settings_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        
        l_language_options = ctk.CTkLabel(self.settings_frame, text="Languages", 
                                          font=ctk.CTkFont(size=Style.LABEL_FONT["size"],
                                                           weight=Style.LABEL_FONT["weight"]))
        l_language_options.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        self.language_optionsmenu = ctk.CTkOptionMenu(self.settings_frame, values=self.lang_options, 
                                             command=self._switch_lang)
        self.language_optionsmenu.set(self.locale_.language_name)
        self.language_optionsmenu.place(relx=0.5, rely=0.26, anchor=tk.CENTER)

    def _exit_handler(self, restart=False):
        if AppHelper._confirm_with_messagebox(exit_=True, restart=restart):
            self.destroy()
        if restart:
            AppHelper.start_app()

    def _switch_lang(self, lang):
        if self.lang_db[lang] == cfg.get("m", "language"):
            AppHelper._show_messagebox(same_lang=True)
            return
        
        AppHelper._update_config("m", "language", self.lang_db[lang])
        self._exit_handler(restart=True)


class AppHelper:
    @staticmethod
    def start_app():
        global cfg
        cfg = ConfigParser()
        cfg.read(Paths.CONFIG_PATH)
        
        if int(cfg.get("misc", "first_time_launch")):
            language = locale.getlocale()[0]
        else:
            language = cfg.get("m", "language")
        locale_ = Locale.parse(language)
        
        # gettext.translation("messages", Paths.LOCALES_PATH, languages=[language]).install()
        
        app = Home(AppHelper._get_language_options(), locale_)
        AppHelper._update_config("misc", "first_time_launch", "0")
        
        app.mainloop()
    
    @staticmethod
    def _confirm_with_messagebox(exit_=False, restart=False):
        if exit_ & restart:
            if tk.messagebox.askyesno("Restart", "Do you want to restart the app?"):
                return True
        
        if exit_ & ~restart:
            if tk.messagebox.askyesno("Exit", "Do you want to exit the app?"):
                return True
        
        return False
    
    @staticmethod
    def _show_messagebox(same_lang=False):
        if same_lang:
            tk.messagebox.showerror("Error", "This language is already selected.")
    
    @staticmethod
    def _update_config(section, option, value):
        cfg[section][option] = value
        
        with open(Paths.CONFIG_PATH, "w") as f:
            cfg.write(f)
            
    @staticmethod
    def _get_language_options():
        lang_db = dict()
        lang_options = list()
        
        locales = sorted(os.listdir(Paths.LOCALES_PATH))
        locales.remove("base.pot")
        
        i = 0
        for file_name in locales:
            lang_options.append(Locale.parse(file_name).language_name)
            lang_db[lang_options[i]] = file_name
            i += 1
        
        return [lang_db, lang_options]
    
    
if __name__ == "__main__":
    AppHelper.start_app()
