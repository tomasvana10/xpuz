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
    CWORD_IMG_LIGHT_PATH = Path(__file__).resolve().parents[1] / "assets/images/cword_img_light.png"
    CWORD_IMG_DARK_PATH = Path(__file__).resolve().parents[1] / "assets/images/cword_img_dark.png"

class Colour:
    class Global:
        EXIT_BUTTON = "#ED3B4D"
        EXIT_BUTTON_HOVER = "#BF0013"
        
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
        self.base_eng_appearances = ["light", "dark", "system"]
        self.cword_browser_opened = False
        ctk.set_appearance_mode(cfg.get("m", "appearance"))
        ctk.set_default_color_theme(cfg.get("m", "theme"))
        ctk.set_widget_scaling(float(cfg.get("m", "scale")))
        
        self.protocol("WM_DELETE_WINDOW", self._exit_handler)
        
        self._make_frames()
        self._place_frames()
        self._make_content()
        self._place_content()

    def _make_frames(self):
        self.container = ctk.CTkFrame(self)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.container.grid_rowconfigure(0, weight=1)
        
        self.settings_frame = ctk.CTkFrame(self.container, 
                                           fg_color=(Colour.Light.FRAME_R, Colour.Dark.FRAME_R),
                                           corner_radius=0)
        
        self.cword_opts_frame = ctk.CTkFrame(self.container, 
                                             fg_color=(Colour.Light.FRAME_L, Colour.Dark.FRAME_L), 
                                             corner_radius=0)
    
    def _place_frames(self):
        self.container.pack(fill=tk.BOTH, expand=True)
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.cword_opts_frame.grid(row=0, column=0, sticky="nsew")

    def _make_content(self):
        self.title = ctk.CTkLabel(self.cword_opts_frame, text="Crossword Puzzle", font=ctk.CTkFont(
                             size=Style.TITLE_FONT["size"],
                             weight=Style.TITLE_FONT["weight"]))
        
        self.cword_img = ctk.CTkLabel(self.cword_opts_frame, text="", 
                                 image=ctk.CTkImage(light_image=Image.open(Paths.CWORD_IMG_LIGHT_PATH),
                                                    dark_image=Image.open(Paths.CWORD_IMG_DARK_PATH),
                                                    size=(453, 154)))
        
        self.b_open_cword_browser = ctk.CTkButton(self.cword_opts_frame, text="View your crosswords",
                                                  command=self.open_cword_browser, width=175, 
                                                  height=50)
        
        self.b_close_app = ctk.CTkButton(self.cword_opts_frame, text="Exit the app",
                                         command=self._exit_handler, width=175, height=50, 
                                         fg_color=Colour.Global.EXIT_BUTTON,
                                         hover_color=Colour.Global.EXIT_BUTTON_HOVER)

        self.settings_label = ctk.CTkLabel(self.settings_frame, text="Global Settings", 
                                      font=ctk.CTkFont(size=Style.SUBHEADING_FONT["size"],
                                                       slant=Style.SUBHEADING_FONT["slant"]))        
        
        self.l_language_optionsmenu = ctk.CTkLabel(self.settings_frame, text="Languages", 
                                          font=ctk.CTkFont(size=Style.LABEL_FONT["size"],
                                                           weight=Style.LABEL_FONT["weight"]))
        self.language_optionsmenu = ctk.CTkOptionMenu(self.settings_frame, values=self.lang_options, 
                                             command=self.switch_lang)
        self.language_optionsmenu.set(self.locale_.language_name)
        
        self.l_scale_optionmenu = ctk.CTkLabel(self.settings_frame, text="Size", 
                                      font=ctk.CTkFont(size=Style.LABEL_FONT["size"],
                                                       weight=Style.LABEL_FONT["weight"]))
        self.scale_optionmenu = ctk.CTkOptionMenu(self.settings_frame, 
                                             values=[str(round(num * 0.1, 1)) for num in range(7, 21)],
                                             command=self.change_scale)
        self.scale_optionmenu.set(cfg.get("m", "scale"))
        
        self.appearances = ["light", "dark", "system"] # make sure to mark for translation later
        self.l_appearance_optionmenu = ctk.CTkLabel(self.settings_frame, text="Appearance", 
                                      font=ctk.CTkFont(size=Style.LABEL_FONT["size"],
                                                       weight=Style.LABEL_FONT["weight"]))
        self.appearance_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=self.appearances, 
                                             command=self.change_appearance)
        self.appearance_optionmenu.set(cfg.get("m", "appearance"))

    def _place_content(self):
        self.title.place(relx=0.5, rely=0.1, anchor="c")
        self.cword_img.place(relx=0.5, rely=0.35, anchor="c")
        self.b_open_cword_browser.place(relx=0.5, rely=0.65, anchor="c")
        self.b_close_app.place(relx=0.5, rely=0.79, anchor="c")
        self.settings_label.place(relx=0.5, rely=0.1, anchor="c")
        self.l_language_optionsmenu.place(relx=0.5, rely=0.2, anchor="c")
        self.language_optionsmenu.place(relx=0.5, rely=0.26, anchor="c")
        self.l_scale_optionmenu.place(relx=0.5, rely=0.4, anchor="c")
        self.scale_optionmenu.place(relx=0.5, rely=0.46, anchor="c")
        self.l_appearance_optionmenu.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        self.appearance_optionmenu.place(relx=0.5, rely=0.66, anchor=tk.CENTER)

    def open_cword_browser(self):
        self.cword_browser = CrosswordBrowser(self)

    def reopen_app(self):
        self.cword_browser.destroy()
        self._make_frames()
        self._place_frames()
        self._make_content()
        self._place_content()

    def _exit_handler(self, restart=False):
        if AppHelper.confirm_with_messagebox(exit_=True, restart=restart):
            self.destroy()
        if restart:
            AppHelper.start_app()

    def change_appearance(self, appearance):
        if appearance == cfg.get("m", "appearance"):
            AppHelper.show_messagebox(same_appearance=True)
            return
        
        eng_appearance_name = self.base_eng_appearances[self.appearances.index(appearance)]
        ctk.set_appearance_mode(eng_appearance_name)
        AppHelper._update_config("m", "appearance", eng_appearance_name)

    def change_scale(self, scale):
        if scale == cfg.get("m", "scale"):
            AppHelper.show_messagebox(same_scale=True)
            return
        
        ctk.set_widget_scaling(float(scale))
        AppHelper._update_config("m", "scale", scale)
        
    def switch_lang(self, lang):
        if self.lang_db[lang] == cfg.get("m", "language"):
            AppHelper.show_messagebox(same_lang=True)
            return
        
        AppHelper._update_config("m", "language", self.lang_db[lang])
        self._exit_handler(restart=True)


class CrosswordBrowser(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master.container.pack_forget()
        self.pack(expand=True, fill=tk.BOTH)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._make_content()
        self._place_content()
    
    def _make_content(self):
        self.scroll_frame = ctk.CTkFrame(self, fg_color="red")
    
    def _place_content(self):
        self.scroll_frame.grid(row=0, column=0, sticky="ew")
        
    def return_home(self):
        self.pack_forget()
        self.master.reopen_app()
        

class CrosswordPreviewBlock(ctk.CTkFrame):
    def __init__(self):
        ...


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
        
        # gettext.translation("messages", localedir=Paths.LOCALES_PATH, languages=[locale_.language]).install()
        
        app = Home(AppHelper._get_language_options(), locale_)
        AppHelper._update_config("misc", "first_time_launch", "0")
        
        app.mainloop()
    
    @staticmethod
    def confirm_with_messagebox(exit_=False, restart=False):
        if exit_ & restart:
            if tk.messagebox.askyesno("Restart", "Are you sure you want to restart the app?"):
                return True
        
        if exit_ & ~restart:
            if tk.messagebox.askyesno("Exit", "Are you sure you want to exit the app?"):
                return True
        
        return False
    
    @staticmethod
    def show_messagebox(same_lang=False, same_scale=False, same_appearance=False):
        if same_lang:
            tk.messagebox.showerror("Error", "This language is already selected.")
        
        if same_scale:
            tk.messagebox.showerror("Error", "This size is already selected.")
        
        if same_appearance:
            tk.messagebox.showerror("Error", "This appearance is already selected.")
    
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