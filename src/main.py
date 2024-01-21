import tkinter as tk 
import tkinter.messagebox
import gettext
import locale
import json
import os
from typing import List, Dict, Tuple, Union
from pprint import pprint

import darkdetect
import customtkinter as ctk 
from configparser import ConfigParser
from babel import Locale
from PIL import Image

import cword_gen as cwg
from cword_gen import Crossword, CrosswordHelper
from constants import (
    Paths, Colour, Fonts, CrosswordDifficulties, CrosswordStyle, BaseEngStrings
)


class Home(ctk.CTk):
    '''The `Home` class acts as a homescreen for the program, providing global setting configuration,
    exit functionality and the ability to view the currently available crossword puzzles.
    '''
    def __init__(self, 
                 lang_info: List[Union[Dict[str, str], List[str]]], 
                 locale_: Locale, 
                 cfg: ConfigParser
                 ) -> None:
        super().__init__()
        self.locale_ = locale_ 
        self.cfg = cfg 
        
        self.localised_lang_db, self.localised_langs = lang_info # Refer to `AppHelper._get_language_options`
        self.title("Crossword Puzzle")
        self.geometry("800x600")
        
        ctk.set_appearance_mode(self.cfg.get("m", "appearance"))
        ctk.set_default_color_theme(self.cfg.get("m", "theme"))
        ctk.set_widget_scaling(float(self.cfg.get("m", "scale")))
        
        self.protocol("WM_DELETE_WINDOW", self._exit_handler)
        
        self.generate_screen()

    def _make_frames(self) -> None:
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
    
    def _place_frames(self) -> None:
        self.container.pack(fill=tk.BOTH, expand=True)
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.cword_opts_frame.grid(row=0, column=0, sticky="nsew")

    def _make_content(self) -> None:
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
        self.language_optionsmenu = ctk.CTkOptionMenu(self.settings_frame, values=self.localised_langs, 
                                             command=self.switch_lang)
        self.language_optionsmenu.set(self.locale_.language_name)
        
        self.l_scale_optionmenu = ctk.CTkLabel(self.settings_frame, text="Size", 
                                      font=ctk.CTkFont(size=Fonts.LABEL_FONT["size"],
                                                       weight=Fonts.LABEL_FONT["weight"]))
        self.scale_optionmenu = ctk.CTkOptionMenu(self.settings_frame, 
                                             values=[str(round(num * 0.1, 1)) for num in range(7, 21)],
                                             command=self.change_scale)
        self.scale_optionmenu.set(self.cfg.get("m", "scale"))
        
        self.appearances: List[str] = ["light", "dark", "system"] # NOTE: mark for translation later
        self.l_appearance_optionmenu = ctk.CTkLabel(self.settings_frame, text="Appearance", 
                                      font=ctk.CTkFont(size=Fonts.LABEL_FONT["size"],
                                                       weight=Fonts.LABEL_FONT["weight"]),
                                      bg_color="transparent")
        self.appearance_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=self.appearances, 
                                             command=self.change_appearance)
        self.appearance_optionmenu.set(self.cfg.get("m", "appearance"))

    def _place_content(self) -> None:
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

    def open_cword_browser(self) -> None:
        '''Remove all homescreen widgets and instantiate the `CrosswordBrowser`.'''
        self.container.pack_forget()
        self.cword_browser = CrosswordBrowser(self)

    def close_cword_browser(self) -> None:
        '''Remove all `CrosswordBrowser` widgets and regenerate the main screen.'''
        self.cword_browser.pack_forget()
        self.generate_screen()
    
    def generate_screen(self) -> None:
        self._make_frames()
        self._place_frames()
        self._make_content()
        self._place_content()

    def _exit_handler(self, 
                      restart: bool = False
                      ) -> None:
        '''Called when the event: "WM_DELETE_WINDOW" occurs or when the the program must be restarted,
        in which case the `restart` default parameter is overridden.
        '''
        if AppHelper.confirm_with_messagebox(exit_=True, restart=restart): # If user wants to exit/restart
            self.quit()
        if restart:
            AppHelper.start_app()

    def change_appearance(self, 
                          appearance: str
                          ) -> None:
        '''Ensures the user is not selecting the same appearance, then sets the appearance. Some 
        list indexing is required to make the program compatible with non-english languages.
        '''
        if appearance == self.cfg.get("m", "appearance"):
            AppHelper.show_messagebox(same_appearance=True)
            return
        
        # Must be done because you cannot do `ctk.set_appearance_mode("نظام")`, for example
        eng_appearance_name = BaseEngStrings.BASE_ENG_APPEARANCES[self.appearances.index(appearance)]
        ctk.set_appearance_mode(eng_appearance_name)
        AppHelper._update_config(self.cfg, "m", "appearance", eng_appearance_name)

    def change_scale(self, 
                     scale: str
                     ) -> None:
        '''Ensures the user is not selecting the same scale, then sets the scale.'''
        # NOTE: Will prob need the same index comparisons as the change_appearance function when 
        # configuring digits to be accurate to the current locale.
        if scale == self.cfg.get("m", "scale"):
            AppHelper.show_messagebox(same_scale=True)
            return
        
        ctk.set_widget_scaling(float(scale))
        AppHelper._update_config(self.cfg, "m", "scale", scale)
        
    def switch_lang(self, 
                    lang: str
                    ) -> None:
        '''Ensures the user is not selecting the same language, then creates a new `locale_` variable
        based on the English name of the language (retrieved from `self.localised_lang_db`). The method then
        installs a new set of translations with gettext and regenerates the content of the GUI.'''
        if self.localised_lang_db[lang] == self.cfg.get("m", "language"):
            AppHelper.show_messagebox(same_lang=True)
            return
        
        AppHelper._update_config(self.cfg, "m", "language", self.localised_lang_db[lang])
        self.locale_ = Locale.parse(self.cfg.get("m", "language"))
        # gettext.translation(...).install()  when I compile all the locales
        self.container.pack_forget()
        self.generate_screen()


class CrosswordBrowser(ctk.CTkFrame):
    '''Provides an interface to view available crosswords, set a preference for the word count,
    generate a crossword (using `cword_gen`) based on the selected parameters, and launch the 
    crossword webapp (work in progress) to complete them.
    '''
    def __init__(self, 
                 master: Home
                 ) -> None:
        super().__init__(master)
        self.master = master
        self.configure(fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        self.pack(expand=True, fill="both")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.cword_launch_options_enabled: bool = False
        self.cword_game_loaded: bool = False
        
        # Integer variables representing what crossword block the user has selected and their 
        # selected word count preference.
        self.selected_block = ctk.IntVar()
        self.selected_block.set(-1)
        self.word_count_preference = ctk.IntVar()
        self.word_count_preference.set(-1)
        
        self._make_content()
        self._place_content()
        self._generate_crossword_blocks()
    
    def _make_content(self) -> None:
        self.center_container = ctk.CTkFrame(self)
        self.horizontal_scroll_frame = ctk.CTkScrollableFrame(self.center_container, 
                                                              orientation="horizontal",
                                                              fg_color=(Colour.Light.SUB,
                                                                        Colour.Dark.SUB),
                                                              scrollbar_button_color=(Colour.Light.MAIN,
                                                                                      Colour.Dark.MAIN),
                                                              corner_radius=0)

        self.l_title = ctk.CTkLabel(self, text="Crossword Browser", 
                                  font=ctk.CTkFont(size=Fonts.TITLE_FONT["size"],
                                                   weight=Fonts.TITLE_FONT["weight"]))
        
        self.b_go_to_home = ctk.CTkButton(self, text="Go back", command=self.go_to_home, width=175, 
                                          height=50, fg_color=Colour.Global.EXIT_BUTTON,
                                          hover_color=Colour.Global.EXIT_BUTTON_HOVER)
        
        self.b_load_selected_cword = ctk.CTkButton(self, text="Load selected crossword", width=175, 
                                                   height=50, command=self.load_selected_cword, 
                                                   state="disabled")
        
        self.l_word_count_preferences = ctk.CTkLabel(self, text="Word count preferences", 
                                                     font=ctk.CTkFont(size=Fonts.BOLD_LABEL_FONT["size"],
                                                                      weight=Fonts.BOLD_LABEL_FONT["weight"]),
                                                     text_color_disabled=(Colour.Light.TEXT_DISABLED,
                                                                          Colour.Dark.TEXT_DISABLED),
                                                     state="disabled") 
        
        self.custom_word_count_optionmenu = ctk.CTkOptionMenu(self, state="disabled")
        self.custom_word_count_optionmenu.set("Select word count")
        
        self.radiobutton_max_word_count = ctk.CTkRadioButton(self, text=f"Maximum: ",
                    variable=self.word_count_preference,
                    value=0, state="disabled", corner_radius=1,
                    command=lambda: self._on_word_count_radiobutton_selection("max"))
        
        self.radiobutton_custom_word_count = ctk.CTkRadioButton(self, text="Custom", 
                    variable=self.word_count_preference,
                    value=1, state="disabled", corner_radius=1,
                    command=lambda: self._on_word_count_radiobutton_selection("custom"))
    
    def _place_content(self) -> None:
        self.center_container.pack(anchor="c", expand=True, fill="x")
        self.horizontal_scroll_frame.pack(expand=True, fill="both")
        self.l_title.place(relx=0.5, rely=0.1, anchor="c")
        self.b_go_to_home.place(relx=0.5, rely=0.2, anchor="c")
        self.b_load_selected_cword.place(relx=0.65, rely=0.85, anchor="c")
        self.l_word_count_preferences.place(relx=0.34, rely=0.745, anchor="c")
        self.radiobutton_max_word_count.place(relx=0.315, rely=0.8, anchor="c")
        self.radiobutton_custom_word_count.place(relx=0.315, rely=0.875, anchor="c")
        self.custom_word_count_optionmenu.place(relx=0.345, rely=0.935, anchor="c")
     
    def _on_word_count_radiobutton_selection(self, 
                                    button_name: str
                                    ) -> None: 
        '''Based on what radiobutton called this function, the custom word count optionmenu will
        either be disabled or enabled. If the crossword game is not yet loaded, this method will also
        enable the launch button.
        '''
        if button_name == "max":
            self.custom_word_count_optionmenu.configure(state="disabled")
            self.custom_word_count_optionmenu.set("Select word count")
        else:
            self.custom_word_count_optionmenu.configure(state="normal")
            self.custom_word_count_optionmenu.set("3")
        
        if not self.cword_game_loaded:
            self.b_load_selected_cword.configure(state="normal")
     
    def load_selected_cword(self) -> None:
        '''Load the selected crossword based on the selected word count option (retrieved from the
        `word_count_preference` IntVar). This method then loads the definitions based on the current
        crosswords name, instantiates a crossword object, finds the best crossword using
        `CrosswordHelper.find_best_crossword`, and launches the interactive web app (work in progress).
        
        NOTE: The crossword information that this function accesses is saved whenever a new crossword
        block is selected (by the `_on_cword_selection` function)
        '''
        if self.word_count_preference.get() == 0: # Just get the max word count
            chosen_word_count = self.selected_cword_word_count
        elif self.word_count_preference.get() == 1: # Get the selected word count from the option menu
            chosen_word_count = int(self.custom_word_count_optionmenu.get())

        definitions = cwg.CrosswordHelper.load_definitions(self.selected_cword_name)
        crossword = cwg.Crossword(definitions=definitions, word_count=chosen_word_count,
                                  name=self.selected_cword_name)
        crossword = cwg.CrosswordHelper.find_best_crossword(crossword)
        
        self.cword_game_loaded: bool = True
        
        # ... work in progress
            
    def _generate_crossword_blocks(self) -> None:
        '''Generates a variable amount of `CrosswordInfoBlock` instances based on how many crosswords
        are available, then packs them into `self.horizontal_scroll_frame`.
        '''
        self.blocks_sequence = list() 
        i = 0
        for file_name in os.listdir(Paths.CWORDS_PATH):
            if file_name.startswith("."): # Stupid hidden OS files
                continue
            block = CrosswordInfoBlock(self.horizontal_scroll_frame, self, file_name, i)
            block.pack(side="left", padx=5, pady=(5, 0))
            self.blocks_sequence.append(file_name)
            i += 1
    
    def _enable_cword_launch_options(self) -> None:
        '''Configure all the word_count preference widgets to an interactive state (when the user
        selects a crossword to configure).
        '''
        self.l_word_count_preferences.configure(state="normal")
        self.radiobutton_max_word_count.configure(state="normal")
        self.radiobutton_custom_word_count.configure(state="normal")
    
    def _on_cword_selection(self, 
                            name: str, 
                            word_count: int
                            ) -> None:
        '''Called by an instance of `CrosswordInfoBlock`, which passes the data for its given crossword 
        into this method. The method then saves this data, deselects any previous word count radiobutton
        selections, reconfigures the values of the custom word count optionmenu to be compatible with
        the newly selected crossword, and reconfigures the max word count label to show the correct
        maximum word count.
        '''
        if not self.cword_launch_options_enabled:
            self._enable_cword_launch_options()
            self.cword_launch_options_enabled = True

        self.word_count_preference.set(-1)
        self.selected_cword_name = name
        self.selected_cword_word_count = word_count
        self.custom_word_count_optionmenu.configure(values=[str(num) for num in range(3, word_count + 1)])
        self.radiobutton_max_word_count.configure(text=f"Maximum: {word_count}")
    
    def go_to_home(self) -> None:
        '''Removes the content of `CrosswordBrowser` and regenerates the `Home` classes content. This
        must be done outside of this class.
        '''
        self.master.close_cword_browser()


class CrosswordInfoBlock(ctk.CTkFrame):
    '''A frame containing a crosswords name, as well data read from `cwords/<cword-name>/info.json`, 
    including total definitions/word count, difficulty, and a symbol to prefix the crosswords name.
    A variable amount of these is created and packed into `CrosswordBrowser.horizontal_scroll_frame`
    depending on how many available crosswords there are.
    '''
    def __init__(self, 
                 container: ctk.CTkFrame, # `CrosswordBrowser.horizontal_scroll_frame`
                 master: CrosswordBrowser, 
                 name: str, 
                 value: int # Used for `self.radiobutton_selector`
                 ) -> None: 
        super().__init__(container)
        self.configure(fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN), 
                       border_color=(Colour.Light.SUB, Colour.Dark.SUB), border_width=3)
        self.master = master
        self.name = name
        self.value = value
        self.info = AppHelper._load_cword_info(name=name)
        
        self._make_content()
        self._place_content()
        
    def _make_content(self) -> None:
        # Using a textbox because a label is impossible to wrap especially with custom widget scaling.
        self.name_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=Fonts.SUBHEADING_FONT["size"],
                                                                  slant=Fonts.SUBHEADING_FONT["slant"]),
                                             wrap="word", fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
                                             scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        self.name_textbox.insert(1.0, f"{self.info['symbol']} {self.name.title()}")
        self.name_textbox.configure(state="disabled")

        self.l_total_words = ctk.CTkLabel(self, text=f"Total words: {self.info['total_definitions']}")
        
        self.l_difficulty = ctk.CTkLabel(self, 
                    text=f"Difficulty: {CrosswordDifficulties.DIFFICULTIES[self.info['difficulty']]}")
        
        self.radiobutton_selector = ctk.CTkRadioButton(self, text="Select", corner_radius=1,
                        variable=self.master.selected_block, 
                        value=self.value, 
                        # Pass the necessary info to `self.master._on_cword_selection` so it can
                        # appropriately configure the word count preferences for the user.
                        command=lambda name=self.name, word_count=self.info["total_definitions"]: \
                            self.master._on_cword_selection(name, word_count))
    
    def _place_content(self) -> None:
        self.name_textbox.place(relx=0.5, rely=0.2, anchor="c", relwidth=0.9, relheight=0.21)
        self.l_total_words.place(relx=0.5, rely=0.47, anchor="c")
        self.l_difficulty.place(relx=0.5, rely=0.58, anchor="c")
        self.radiobutton_selector.place(relx=0.5, rely=0.76, anchor="c")
        
     
class AppHelper:
    '''Miscellaneous functions that aid the other classes of `main.py`.'''
    @staticmethod
    def start_app() -> None:
        '''Initialise the cfg (config) object and the locale_ object, then instantiate the `Home`
        class with these objects and language information returned from `AppHelper._get_language_options`.
        '''
        cfg = ConfigParser()
        cfg.read(Paths.CONFIG_PATH)
        
        if int(cfg.get("misc", "first_time_launch")): # Detect locale (first time launch)
            language: str = locale.getlocale()[0]
        else: # Just read from config
            language: str = cfg.get("m", "language")
        locale_: Locale = Locale.parse(language)
        
        # gettext.translation("messages", localedir=Paths.LOCALES_PATH, languages=[locale_.language]).install()
        
        AppHelper._update_config(cfg, "m", "language", locale_.language)
        AppHelper._update_config(cfg, "misc", "first_time_launch", "0")
        app = Home(AppHelper._get_language_options(), locale_, cfg)
        
        app.mainloop()
    
    @staticmethod
    def confirm_with_messagebox(exit_: bool = False, 
                                restart: bool = False
                                ) -> bool:
        '''Display appropriate confirmation messageboxes to the user, called by `Home._exit_handler`.'''
        if exit_ & restart:
            if tk.messagebox.askyesno("Restart", "Are you sure you want to restart the app?"):
                return True
        
        if exit_ & ~restart:
            if tk.messagebox.askyesno("Exit", "Are you sure you want to exit the app?"):
                return True
        
        return False
    
    @staticmethod
    def show_messagebox(same_lang: bool = False, 
                        same_scale: bool = False, 
                        same_appearance: bool = False
                        ) -> None:
        '''Display appropriate error messages when a user attempts to select an already selected
        global settings options.
        '''
        if same_lang:
            tk.messagebox.showerror("Error", "This language is already selected.")
        
        if same_scale:
            tk.messagebox.showerror("Error", "This size is already selected.")
        
        if same_appearance:
            tk.messagebox.showerror("Error", "This appearance is already selected.")
    
    @staticmethod
    def _update_config(cfg, 
                       section: str, 
                       option: str, 
                       value: str
                       ) -> None:
        '''Update `cfg` at the given section, option and value, then write it to `config.ini`.'''
        cfg[section][option] = value
        
        with open(Paths.CONFIG_PATH, "w") as f:
            cfg.write(f)
            
    @staticmethod
    def _get_language_options() -> None:
        '''Gather a dictionary that maps each localised language name to its english acronym, and a list
        that contains all of the localised language names. This data is derived from `Paths.LOCALES_PATH`.'''
        localised_lang_db = dict() # Used to retrieve the language code for the selected language
        ''' example:
        {"አማርኛ": "am",}
        '''
        localised_langs = list() # Used in the language selection optionmenu
        ''' example:
        ["አማርኛ", "عربي"]
        '''
        
        locales = sorted(os.listdir(Paths.LOCALES_PATH))
        locales.remove("base.pot")
        
        i = 0
        for file_name in locales:
            localised_langs.append(Locale.parse(file_name).language_name)
            localised_lang_db[localised_langs[i]] = file_name
            i += 1
        
        return [localised_lang_db, localised_langs]
    
    @staticmethod
    def _load_cword_info(name: str) -> Dict[str, Union[str, int]]:
        '''Load the `info.json` file for a crossword. Called by an instance of `CrosswordInfoBlock`.'''
        with open(f"{Paths.CWORDS_PATH}/{name}/info.json") as file:
            info = json.load(file)
        
        return info
    
    
if __name__ == "__main__":
    AppHelper.start_app()