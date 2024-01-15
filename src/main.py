import tkinter as tk 
import tkinter.messagebox
import locale
import os
import json
from configparser import ConfigParser

import gettext
import darkdetect
import customtkinter as ctk 
from babel import Locale
from PIL import Image

import cword_gen as cwg
from constants import Paths, Colour, Fonts, Difficulties, OtherConstants


class Home(ctk.CTk):
    def __init__(self, lang_info, locale_, cfg):
        super().__init__()
        self.locale_ = locale_ 
        self.cfg = cfg
        
        self.lang_db, self.lang_options = lang_info
        self.title("Crossword Puzzle")
        self.geometry("800x600")
        
        ctk.set_appearance_mode(self.cfg.get("m", "appearance"))
        ctk.set_default_color_theme(self.cfg.get("m", "theme"))
        ctk.set_widget_scaling(float(self.cfg.get("m", "scale")))
        
        self.protocol("WM_DELETE_WINDOW", self._exit_handler)
        
        self.generate_screen()

    def _make_frames(self):
        self.container = ctk.CTkFrame(self)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.container.grid_rowconfigure(0, weight=1)
        
        self.settings_frame = ctk.CTkFrame(self.container, 
                                           fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
                                           corner_radius=0)
        
        self.cword_opts_frame = ctk.CTkFrame(self.container, 
                                             fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN), 
                                             corner_radius=0)
    
    def _place_frames(self):
        self.container.pack(fill=tk.BOTH, expand=True)
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.cword_opts_frame.grid(row=0, column=0, sticky="nsew")

    def _make_content(self):
        self.l_title = ctk.CTkLabel(self.cword_opts_frame, text="Crossword Puzzle", 
                                  font=ctk.CTkFont(size=Fonts.TITLE_FONT["size"],
                                                   weight=Fonts.TITLE_FONT["weight"]))
        
        self.cword_img = ctk.CTkLabel(self.cword_opts_frame, text="", 
                                 image=ctk.CTkImage(light_image=Image.open(Paths.CWORD_IMG_LIGHT_PATH),
                                                    dark_image=Image.open(Paths.CWORD_IMG_DARK_PATH),
                                                    size=(453, 154)))
        
        self.b_open_cword_browser = ctk.CTkButton(self.cword_opts_frame, text="View crosswords",
                                                  command=self.open_cword_browser, width=175, 
                                                  height=50)
        
        self.b_close_app = ctk.CTkButton(self.cword_opts_frame, text="Exit the app",
                                         command=self._exit_handler, width=175, height=50, 
                                         fg_color=Colour.Global.EXIT_BUTTON,
                                         hover_color=Colour.Global.EXIT_BUTTON_HOVER)

        self.l_settings = ctk.CTkLabel(self.settings_frame, text="Global Settings", 
                                      font=ctk.CTkFont(size=Fonts.SUBHEADING_FONT["size"],
                                                       slant=Fonts.SUBHEADING_FONT["slant"]))        
        
        self.l_language_optionsmenu = ctk.CTkLabel(self.settings_frame, text="Languages", 
                                          font=ctk.CTkFont(size=Fonts.LABEL_FONT["size"],
                                                           weight=Fonts.LABEL_FONT["weight"]))
        self.language_optionsmenu = ctk.CTkOptionMenu(self.settings_frame, values=self.lang_options, 
                                             command=self.switch_lang)
        self.language_optionsmenu.set(self.locale_.language_name)
        
        self.l_scale_optionmenu = ctk.CTkLabel(self.settings_frame, text="Size", 
                                      font=ctk.CTkFont(size=Fonts.LABEL_FONT["size"],
                                                       weight=Fonts.LABEL_FONT["weight"]))
        self.scale_optionmenu = ctk.CTkOptionMenu(self.settings_frame, 
                                             values=[str(round(num * 0.1, 1)) for num in range(7, 21)],
                                             command=self.change_scale)
        self.scale_optionmenu.set(self.cfg.get("m", "scale"))
        
        self.appearances = ["light", "dark", "system"] # make sure to mark for translation later
        self.l_appearance_optionmenu = ctk.CTkLabel(self.settings_frame, text="Appearance", 
                                      font=ctk.CTkFont(size=Fonts.LABEL_FONT["size"],
                                                       weight=Fonts.LABEL_FONT["weight"]))
        self.appearance_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=self.appearances, 
                                             command=self.change_appearance)
        self.appearance_optionmenu.set(self.cfg.get("m", "appearance"))

    def _place_content(self):
        self.l_title.place(relx=0.5, rely=0.1, anchor="c")
        self.cword_img.place(relx=0.5, rely=0.35, anchor="c")
        self.b_open_cword_browser.place(relx=0.5, rely=0.65, anchor="c")
        self.b_close_app.place(relx=0.5, rely=0.79, anchor="c")
        self.l_settings.place(relx=0.5, rely=0.1, anchor="c")
        self.l_language_optionsmenu.place(relx=0.5, rely=0.2, anchor="c")
        self.language_optionsmenu.place(relx=0.5, rely=0.26, anchor="c")
        self.l_scale_optionmenu.place(relx=0.5, rely=0.4, anchor="c")
        self.scale_optionmenu.place(relx=0.5, rely=0.46, anchor="c")
        self.l_appearance_optionmenu.place(relx=0.5, rely=0.6, anchor="c")
        self.appearance_optionmenu.place(relx=0.5, rely=0.66, anchor="c")

    def open_cword_browser(self):
        self.wipe_screen()
        self.cword_browser = CrosswordBrowser(self)

    def close_cword_browser(self):
        self.cword_browser.destroy()
        self.generate_screen()
    
    def generate_screen(self):
        self._make_frames()
        self._place_frames()
        self._make_content()
        self._place_content()
    
    def wipe_screen(self):
        self.container.pack_forget()

    def _exit_handler(self, restart=False):
        if AppHelper.confirm_with_messagebox(exit_=True, restart=restart):
            self.destroy()
        if restart:
            AppHelper.start_app()

    def change_appearance(self, appearance):
        if appearance == self.cfg.get("m", "appearance"):
            AppHelper.show_messagebox(same_appearance=True)
            return
        
        eng_appearance_name = OtherConstants.BASE_ENG_APPEARANCES[self.appearances.index(appearance)]
        ctk.set_appearance_mode(eng_appearance_name)
        AppHelper._update_config(self.cfg, "m", "appearance", eng_appearance_name)

    def change_scale(self, scale):
        if scale == self.cfg.get("m", "scale"):
            AppHelper.show_messagebox(same_scale=True)
            return
        
        ctk.set_widget_scaling(float(scale))
        AppHelper._update_config(self.cfg, "m", "scale", scale)
        
    def switch_lang(self, lang):
        if self.lang_db[lang] == self.cfg.get("m", "language"):
            AppHelper.show_messagebox(same_lang=True)
            return
        
        AppHelper._update_config(self.cfg, "m", "language", self.lang_db[lang])
        self.locale_ = Locale.parse(self.cfg.get("m", "language"))
        self.wipe_screen()
        self.generate_screen()


class CrosswordBrowser(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        self.pack(expand=True, fill="both")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._make_content()
        self._place_content()
        self._generate_crossword_blocks()
    
    def _make_content(self):
        self.container = ctk.CTkFrame(self)
        self.horizontal_scroll_frame = HorizontalScrollFrame(self.container, self.master)
        # pack widgets in self.horizontal_scroll_frame.scrollable_frame with side="left"

        self.l_title = ctk.CTkLabel(self, text="Crossword Browser", 
                                  font=ctk.CTkFont(size=Fonts.TITLE_FONT["size"],
                                                   weight=Fonts.TITLE_FONT["weight"]))
        self.b_go_to_home = ctk.CTkButton(self, text="Go back", command=self.go_to_home, width=175, 
                                          height=50, fg_color=Colour.Global.EXIT_BUTTON,
                                          hover_color=Colour.Global.EXIT_BUTTON_HOVER)
        self.b_load_selected_cword = ctk.CTkButton(self, text="Load selected crossword", width=175, 
                                                   height=50)
    
    def _place_content(self):
        self.container.grid(row=0, column=0, sticky="ew")
        self.horizontal_scroll_frame.pack(expand=True, fill="both")
        self.l_title.place(relx=0.5, rely=0.15, anchor="c")
        self.b_go_to_home.place(relx=0.35, rely=0.8, anchor="c")
        self.b_load_selected_cword.place(relx=0.65, rely=0.8, anchor="c")
     
    def _generate_crossword_blocks(self):
        self.blocks_sequence = list()
        for file_name in os.listdir(Paths.CWORDS_PATH):
            if file_name.startswith("."):
                continue
            block = CrosswordInfoBlock(self.horizontal_scroll_frame.scrollable_frame, name=file_name)
            block.pack(side="left", padx=5)
            self.blocks_sequence.append(file_name)
    
    def go_to_home(self):
        self.destroy()
        self.master.close_cword_browser()


class HorizontalScrollFrame(ctk.CTkFrame):
    def __init__(self, container, master):
        super().__init__(container)
        self.master = master
        h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", 
                                       button_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        h_scrollbar.pack(fill="x", side="bottom", expand=False)
        
        if AppHelper._determine_true_appearance(self.master.cfg) == "light":
            canvas_bg_colour = Colour.Light.SUB
        else:
            canvas_bg_colour = Colour.Dark.SUB
        self.canvas = ctk.CTkCanvas(self, bd=7.5, highlightthickness=1, xscrollcommand=h_scrollbar.set, 
                                    background=canvas_bg_colour)
        self.canvas.pack(side="bottom", fill="both", expand=True)
        self.canvas.bind('<Configure>', self._update_scroll_region)
        h_scrollbar.configure(command=self.canvas.xview)

        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
                                             corner_radius=0)
        self.window_reference = self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="w")

    def _update_scroll_region(self, _):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


class CrosswordInfoBlock(ctk.CTkFrame):
    def __init__(self, container, name): 
        super().__init__(container)
        self.configure(fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
                       border_color=(Colour.Light.SUB, Colour.Dark.SUB),
                       border_width=3)
        info = AppHelper._load_cword_info(name=name)
        l_name_title = ctk.CTkLabel(self, text=f"{info['symbol']} {name.title()}", 
                                    font=ctk.CTkFont(size=Fonts.SUBHEADING_FONT["size"],
                                                     slant=Fonts.SUBHEADING_FONT["slant"]))
        l_total_words = ctk.CTkLabel(self, text=f"Total words: {info['total_definitions']}")
        l_difficulty = ctk.CTkLabel(self, text=f"Difficulty: {Difficulties.DIFFICULTIES[info['difficulty']]}")
        
        l_name_title.place(relx=0.5, rely=0.2, anchor="c")
        l_total_words.place(relx=0.5, rely=0.45, anchor="c")
        l_difficulty.place(relx=0.5, rely=0.55, anchor="c")

     
class AppHelper:
    @staticmethod
    def start_app():
        cfg = ConfigParser()
        cfg.read(Paths.CONFIG_PATH)
        
        if int(cfg.get("misc", "first_time_launch")):
            language = locale.getlocale()[0]
        else:
            language = cfg.get("m", "language")
        locale_ = Locale.parse(language)
        
        # gettext.translation("messages", localedir=Paths.LOCALES_PATH, languages=[locale_.language]).install()
        
        AppHelper._update_config(cfg, "m", "language", locale_.language)
        AppHelper._update_config(cfg, "misc", "first_time_launch", "0")
        app = Home(AppHelper._get_language_options(), locale_, cfg)
        
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
    def _update_config(cfg, section, option, value):
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
    
    @staticmethod
    def _determine_true_appearance(cfg):
        retrieved_appearance = cfg.get("m", "appearance")
        if retrieved_appearance == "system":
            appearance = darkdetect.theme().casefold()
        elif retrieved_appearance == "dark":
            appearance = "dark"
        else:
            appearance = "light"
        
        return appearance
    
    @staticmethod
    def _load_cword_info(name):
        with open(f"{Paths.CWORDS_PATH}/{name}/info.json") as file:
            info = json.load(file)
        
        return info
                 
    
if __name__ == "__main__":
    AppHelper.start_app()
