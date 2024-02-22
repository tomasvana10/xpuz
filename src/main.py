import tkinter as tk 
import tkinter.messagebox
import gettext
import json
import webbrowser
import os
from time import sleep
from copy import deepcopy
from typing import List, Dict, Tuple, Union
from configparser import ConfigParser

import customtkinter as ctk 
from babel import Locale, numbers
from PIL import Image, ImageTk

import cword_gen as cwg
import cword_webapp.app as app
from cword_gen import Crossword, CrosswordHelper
from constants import (
    Paths, Colour, CrosswordDifficulties, CrosswordStyle, CrosswordDirections, BaseEngStrings
)


class Home(ctk.CTk):
    '''The `Home` class acts as a homescreen for the program, providing global setting configuration,
    exit functionality and the ability to view the currently available crossword puzzles.
    '''
    def __init__(self, 
                 lang_info: List[Union[Dict[str, str], List[str]]], 
                 locale: Locale, 
                 cfg: ConfigParser
                 ) -> None:
        super().__init__()
        self.locale: Locale = locale 
        self.cfg: ConfigParser = cfg 
        
        self.localised_lang_db, self.localised_langs = lang_info # Refer to `AppHelper._get_language_options`
        self.protocol("WM_DELETE_WINDOW", self._exit_handler)
        self.title(_("Crossword Puzzle"))
        self.geometry("800x600")
        
        ctk.set_appearance_mode(self.cfg.get("m", "appearance"))
        ctk.set_default_color_theme(self.cfg.get("m", "theme"))
        ctk.set_widget_scaling(float(self.cfg.get("m", "scale")))
        
        self._make_fonts()
        self.generate_screen()

    def _make_fonts(self):
        self.TITLE_FONT = ctk.CTkFont(size=31, weight="bold", slant="roman")
        self.SUBHEADING_FONT = ctk.CTkFont(size=24, weight="normal", slant="italic")
        self.TEXT_FONT = ctk.CTkFont(size=15, weight="normal", slant="roman")
        self.BOLD_TEXT_FONT = ctk.CTkFont(size=15, weight="bold", slant="roman")
        self.CATEGORY_FONT = ctk.CTkFont(size=26, weight="bold", slant="roman")
        self.CWORD_BLOCK_FONT = ctk.CTkFont(size=21, weight="normal", slant="roman")

    def _make_frames(self) -> None:
        self.container = ctk.CTkFrame(self)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.container.grid_rowconfigure(0, weight=1)
        
        self.settings_container = ctk.CTkFrame(self.container, fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
                                           corner_radius=0)
        
        self.cword_opts_container = ctk.CTkFrame(self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN), 
                                             corner_radius=0)
    
    def _place_frames(self) -> None:
        self.container.pack(fill="both", expand=True)
        self.settings_container.grid(row=0, column=1, sticky="nsew")
        self.cword_opts_container.grid(row=0, column=0, sticky="nsew")

    def _make_content(self) -> None:
        self.l_title = ctk.CTkLabel(self.cword_opts_container, text=_("Crossword Puzzle"), 
                                    font=self.TITLE_FONT)
        
        self.cword_img = ctk.CTkLabel(self.cword_opts_container, text="", 
                                      image=ctk.CTkImage(light_image=Image.open(Paths.CWORD_IMG_LIGHT_PATH),
                                                         dark_image=Image.open(Paths.CWORD_IMG_DARK_PATH),
                                                         size=(453, 154)))
        
        self.b_open_cword_browser = ctk.CTkButton(self.cword_opts_container, text=_("View crosswords"),
                                                  command=self.open_cword_browser, width=175, 
                                                  height=50, font=self.TEXT_FONT)
        
        self.b_close_app = ctk.CTkButton(self.cword_opts_container, text=_("Exit the app"),
                                         command=self._exit_handler, width=175, height=50, 
                                         fg_color=Colour.Global.EXIT_BUTTON,
                                         hover_color=Colour.Global.EXIT_BUTTON_HOVER,
                                         font=self.TEXT_FONT)

        self.l_settings = ctk.CTkLabel(self.settings_container, text=_("Global Settings"), 
                                       font=self.SUBHEADING_FONT, wraplength=self.settings_container.winfo_reqwidth())
        
        self.l_language_optionsmenu = ctk.CTkLabel(self.settings_container, text=_("Languages"), 
                                                   font=self.BOLD_TEXT_FONT)
        self.language_optionsmenu = ctk.CTkOptionMenu(self.settings_container, values=self.localised_langs, 
                                                      command=self.switch_lang, font=self.TEXT_FONT)
        self.language_optionsmenu.set(self.locale.language_name)
        
        self.l_scale_optionmenu = ctk.CTkLabel(self.settings_container, text=_("Size"), font=self.BOLD_TEXT_FONT)
        self.scale_optionmenu = ctk.CTkOptionMenu(self.settings_container, font=self.TEXT_FONT,
                                                  command=self.change_scale,
                                                  values=[numbers.format_decimal(str(round(num * 0.1, 1)), 
                                                                                 locale=self.locale) for num in range(7, 16)])
        self.scale_optionmenu.set(numbers.format_decimal(self.cfg.get("m", "scale"), locale=self.locale))
        
        self.appearances: List[str] = [_("light"), _("dark"), _("system")] # NOTE: mark for translation later
        self.l_appearance_optionmenu = ctk.CTkLabel(self.settings_container, text=_("Appearance"), 
                                                    bg_color="transparent", font=self.BOLD_TEXT_FONT)
        self.appearance_optionmenu = ctk.CTkOptionMenu(self.settings_container, values=self.appearances, 
                                                       command=self.change_appearance, font=self.TEXT_FONT)
        self.appearance_optionmenu.set(_(self.cfg.get("m", "appearance")))

    def _place_content(self) -> None:
        self.l_title.place(relx=0.5, rely=0.1, anchor="c")
        self.cword_img.place(relx=0.5, rely=0.35, anchor="c")
        self.b_open_cword_browser.place(relx=0.5, rely=0.65, anchor="c")
        self.b_close_app.place(relx=0.5, rely=0.76, anchor="c")
        self.l_settings.place(relx=0.5, rely=0.1, anchor="c")
        self.l_language_optionsmenu.place(relx=0.5, rely=0.24, anchor="c")
        self.language_optionsmenu.place(relx=0.5, rely=0.30, anchor="c")
        self.l_scale_optionmenu.place(relx=0.5, rely=0.44, anchor="c")
        self.scale_optionmenu.place(relx=0.5, rely=0.5, anchor="c")
        self.l_appearance_optionmenu.place(relx=0.5, rely=0.64, anchor="c")
        self.appearance_optionmenu.place(relx=0.5, rely=0.7, anchor="c")

    def open_cword_browser(self) -> None:
        '''Remove all homescreen widgets and instantiate the `CrosswordBrowser` class'''
        self.container.pack_forget()
        self.cword_browser: object = CrosswordBrowser(self)

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
                      restart: bool = False,
                      webapp_running: bool = False
                      ) -> None:
        '''Called when the event: "WM_DELETE_WINDOW" occurs or when the the program must be restarted,
        in which case the `restart` default parameter is overridden.
        '''
        if AppHelper.confirm_with_messagebox(exit_=True, restart=restart): # If user wants to exit/restart
            try:
                if self.cword_browser.webapp_running: # Web app must be terminated when going to home screen
                    app.terminate_app()
            except: ...
            self.quit()
            
        if restart:
            AppHelper.start_app()

    def change_appearance(self, 
                          appearance: str
                          ) -> None:
        '''Ensures the user is not selecting the same appearance, then sets the appearance. Some 
        list indexing is required to make the program compatible with non-english languages.
        '''
        # Must be done because you cannot do `ctk.set_appearance_mode("نظام")`, for example
        eng_appearance_name: str = BaseEngStrings.BASE_ENG_APPEARANCES[self.appearances.index(appearance)]
        if eng_appearance_name == self.cfg.get("m", "appearance"):
            AppHelper.show_messagebox(same_appearance=True)
            return
        
        ctk.set_appearance_mode(eng_appearance_name)
        AppHelper._update_config(self.cfg, "m", "appearance", eng_appearance_name)

    def change_scale(self, 
                     scale: str
                     ) -> None:
        '''Ensures the user is not selecting the same scale, then sets the scale.'''
        scale = float(numbers.parse_decimal(scale, locale=self.locale))

        if scale == float(self.cfg.get("m", "scale")):
            AppHelper.show_messagebox(same_scale=True)
            return
        
        ctk.set_widget_scaling(scale)
        AppHelper._update_config(self.cfg, "m", "scale", str(scale))
        
    def switch_lang(self, 
                    lang: str
                    ) -> None:
        '''Ensures the user is not selecting the same language, then creates a new `locale` variable
        based on the English name of the language (retrieved from `self.localised_lang_db`). The method then
        installs a new set of translations with gettext and regenerates the content of the GUI.'''
        if self.localised_lang_db[lang] == self.cfg.get("m", "language"):
            AppHelper.show_messagebox(same_lang=True)
            return
        
        AppHelper._update_config(self.cfg, "m", "language", self.localised_lang_db[lang])
        self.locale: Locale = Locale.parse(self.cfg.get("m", "language"))
        gettext.translation("messages", localedir=Paths.LOCALES_PATH, languages=[self.locale.language]).install()
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
        self.webapp_running: bool = False
        
        self.word_count_preference = ctk.IntVar()
        self.word_count_preference.set(-1)
        
        self._make_content()
        self._place_content()
        self._generate_crossword_category_blocks()
    
        if self.master.cfg.get("misc", "cword_browser_opened") == "0": 
            AppHelper.show_messagebox(first_time_opening_cword_browser=True)
            AppHelper._update_config(self.master.cfg, "misc", "cword_browser_opened", "1")
            
    def _make_content(self) -> None:
        self.center_container = ctk.CTkFrame(self)
        self.horizontal_scroll_frame = ctk.CTkScrollableFrame(self.center_container, 
                                                              orientation="horizontal",
                                                              fg_color=(Colour.Light.SUB,
                                                                        Colour.Dark.SUB),
                                                              scrollbar_button_color=(Colour.Light.MAIN,
                                                                                      Colour.Dark.MAIN),
                                                              corner_radius=0)
        self.horizontal_scroll_frame.bind_all("<MouseWheel>", self._handle_scroll)
        self.button_container = ctk.CTkFrame(self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        self.preference_container = ctk.CTkFrame(self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        self.preference_container.grid_columnconfigure((0, 1), weight=0)

        self.l_title = ctk.CTkLabel(self, text=_("Crossword Browser"), font=self.master.TITLE_FONT)
        
        self.b_go_to_home = ctk.CTkButton(self, text=_("Go back"), command=self.go_to_home, width=175, 
                                          height=50, fg_color=Colour.Global.EXIT_BUTTON,
                                          hover_color=Colour.Global.EXIT_BUTTON_HOVER, 
                                          font=self.master.TEXT_FONT)
        
        self.b_load_selected_cword = ctk.CTkButton(self.button_container, text=_("Load crossword"), 
                                                   height=50, command=self.load_selected_cword, 
                                                   state="disabled", font=self.master.TEXT_FONT)
        
        self.b_open_cword_webapp = ctk.CTkButton(self.button_container, text=_("Open web app"),
                                                 height=50, command=self.open_cword_webapp,
                                                 state="disabled", font=self.master.TEXT_FONT)
        
        self.b_terminate_cword_webapp = ctk.CTkButton(self.button_container, text=_("Terminate web app"),
                                             height=50, command=self.terminate_cword_webapp,
                                             fg_color=Colour.Global.EXIT_BUTTON,
                                             hover_color=Colour.Global.EXIT_BUTTON_HOVER,
                                             state="disabled", font=self.master.TEXT_FONT)
        
        self.l_word_count_preferences = ctk.CTkLabel(self.preference_container, text=_("Word count preferences"), 
                                                     state="disabled", font=self.master.BOLD_TEXT_FONT,
                                                     text_color_disabled=(Colour.Light.TEXT_DISABLED,
                                                                          Colour.Dark.TEXT_DISABLED))
        
        self.custom_word_count_optionmenu = ctk.CTkOptionMenu(self.preference_container, state="disabled",
                                                              font=self.master.TEXT_FONT)
        self.custom_word_count_optionmenu.set(_("Select word count"))
        
        self.radiobutton_max_word_count = ctk.CTkRadioButton(
                                    self.preference_container, 
                                    text=f"{_("Maximum")}: ",
                                    variable=self.word_count_preference,
                                    value=0, state="disabled", corner_radius=1,
                                    command=lambda: self._on_word_count_radiobutton_selection("max"),
                                    font=self.master.TEXT_FONT)
        
        self.radiobutton_custom_word_count = ctk.CTkRadioButton(
                                self.preference_container,
                                text=_("Custom"), 
                                variable=self.word_count_preference,
                                value=1, state="disabled", corner_radius=1,
                                command=lambda: self._on_word_count_radiobutton_selection("custom"),
                                font=self.master.TEXT_FONT)
    
    def _place_content(self) -> None:
        self.center_container.pack(anchor="c", expand=True, fill="x")
        self.horizontal_scroll_frame.pack(expand=True, fill="both")
        self.button_container.place(relx=0.725, rely=0.84, anchor="c")
        self.preference_container.place(relx=0.3, rely=0.84, anchor="c")
        self.l_title.place(relx=0.5, rely=0.1, anchor="c")
        self.b_go_to_home.place(relx=0.5, rely=0.2, anchor="c")
        self.b_load_selected_cword.grid(row=0, column=0, sticky="nsew", padx=7, pady=7)
        self.b_open_cword_webapp.grid(row=0, column=1, sticky="nsew", padx=7, pady=7)
        self.b_terminate_cword_webapp.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=77.5, pady=7)
        self.l_word_count_preferences.grid(row=0, column=0, columnspan=2, pady=(5, 10))
        self.radiobutton_max_word_count.grid(row=1, column=0, padx=7, pady=7)
        self.radiobutton_custom_word_count.grid(row=2, column=0, padx=7, pady=7)  
        self.custom_word_count_optionmenu.grid(row=3, column=0, padx=7, pady=7)
     
    def _handle_scroll(self, event):
        '''Scroll the center scroll frame only if the viewable width is greater than the scroll region.
        This prevents weird scroll behaviour in cases where the above condition is inverted.
        '''
        scroll_region = self.horizontal_scroll_frame._parent_canvas.cget("scrollregion")
        viewable_width = self.horizontal_scroll_frame._parent_canvas.winfo_width()
        if scroll_region and int(scroll_region.split(" ")[2]) > viewable_width:
            self.horizontal_scroll_frame._parent_canvas.xview("scroll", event.delta, "units")
            
    def _on_word_count_radiobutton_selection(self, 
                                             button_name: str
                                             ) -> None: 
        '''Configure custom word count optionmenu based on radiobutton selection.'''
        if button_name == "max": # User wants max word count, do not let them select custom word count.
            self.custom_word_count_optionmenu.set(_("Select word count"))
            self.custom_word_count_optionmenu.configure(state="disabled")
        else: # User wants custom word count, do not let them select max word count.
            self.custom_word_count_optionmenu.set(f"{str(numbers.format_decimal(3, locale=self.master.locale))}")
            self.custom_word_count_optionmenu.configure(state="normal")
        
        if not self.webapp_running: # Only if they haven't started the web app
            self.b_load_selected_cword.configure(state="normal")
     
    def open_cword_webapp(self) -> None:
        '''Open the crossword web app at a port read from `self.master.cfg`.'''
        webbrowser.open(f"http://127.0.0.1:{self.master.cfg.get('misc', 'webapp_port')}/")
     
    def terminate_cword_webapp(self) -> None:
        '''Appropriately reconfigure the states of the GUIs buttons and terminate the app.'''
        self._rollback_states()
        self.cword_launch_options_enabled: bool = False
        self.webapp_running: bool = False
        try: # This func is used when a category is closed; everything is executed the same except web app termination
            app.terminate_app() 
        except: ...
            
    def _rollback_states(self) -> None:
        self.b_terminate_cword_webapp.configure(state="disabled")
        self.b_open_cword_webapp.configure(state="disabled")
        try: # The user might not have clicked "open" for any categories
            self.selected_category_object.b_close_category.configure(state="normal")
            self.selected_category_object._configure_cword_blocks_state("normal")
        except: ...
        self._configure_cword_launch_options_state("disabled")
        self.radiobutton_max_word_count.configure(text=f"{_("Maximum")}:")
        self.custom_word_count_optionmenu.set(_("Select word count"))
        self.word_count_preference.set(-1)
     
    def _configure_cword_launch_options_state(self, 
                                     state_: str
                                     ) -> None:
        '''Configure all the word_count preference widgets to an either an interactive or disabled
        state (interactive when selecting a crossword, disabled when a crossword has been loaded).
        '''
        self.l_word_count_preferences.configure(state=state_)
        self.radiobutton_max_word_count.configure(state=state_)
        self.radiobutton_custom_word_count.configure(state=state_) 
        self.custom_word_count_optionmenu.configure(state=state_)
    
    def load_selected_cword(self) -> None:
        '''Load the selected crossword based on the selected word count option (retrieved from the
        `word_count_preference` IntVar). This method then loads the definitions based on the current
        crosswords name, instantiates a crossword object, finds the best crossword using
        `CrosswordHelper.find_best_crossword`, and launches the interactive web app via `init_webapp`
        using data retrieved from the crossword instance's attributes.
        
        NOTE: The crossword information that this function accesses is saved whenever a new crossword
        block is selected (by the `_on_cword_selection` function).
        '''
        self.b_load_selected_cword.configure(state="disabled")
        self.selected_category_object.b_close_category.configure(state="disabled")
        self.selected_category_object._configure_cword_blocks_state("disabled")
        self._configure_cword_launch_options_state("disabled")
        self.selected_category_object.selected_block.set(-1)
        self.webapp_running: bool = True
        
        # Max word count / custom word count
        chosen_word_count: int = self.selected_cword_word_count if self.word_count_preference.get() == 0 \
                            else int(self.custom_word_count_optionmenu.get())

        # Load definitions, instantiate a crossword, then find the best crossword using that instance
        definitions: Dict[str, str] = cwg.CrosswordHelper.load_definitions(self.selected_cword_category, self.selected_cword_name, 
                                                                           self.master.locale.language)
        crossword: object = cwg.Crossword(definitions=definitions, word_count=chosen_word_count,
                                          name=self.selected_cword_name)
        crossword: object = cwg.CrosswordHelper.find_best_crossword(crossword)
        
        self._interpret_cword_data(crossword)
        self._init_webapp(crossword)
        
        sleep(1.25) # Must force user to wait before they click, or else the browser might break
        self.b_open_cword_webapp.configure(state="normal")
        self.b_terminate_cword_webapp.configure(state="normal")
        
    def _init_webapp(self, 
                    crossword: cwg.Crossword
                    ) -> None:
        '''Start the flask web app with information from the crossword and other interpreted data'''
        colour_palette: Dict[str, str] = AppHelper._get_colour_palette_for_webapp(ctk.get_appearance_mode())
        app._create_app_process(
            locale=self.master.locale,
            colour_palette=colour_palette,
            json_colour_palette=json.dumps(colour_palette),
            cword_data=crossword.data,
            port=self.master.cfg.get("misc", "webapp_port"), 
            empty=CrosswordStyle.EMPTY,
            name=crossword.name,
            directions=[CrosswordDirections.ACROSS, CrosswordDirections.DOWN],
            # Tuples in intersections must be removed. Changing this in `cworg_gen.py` was annoying,
            # so it is done here instead. 
            intersections=[list(item) if isinstance(item, tuple) else item for \
                          sublist in crossword.intersections for item in sublist],
            word_count=crossword.word_count,
            failed_insertions=crossword.fails,
            dimensions=crossword.dimensions,
            starting_word_positions=self.starting_word_positions,
            starting_word_matrix=self.starting_word_matrix,
            grid=crossword.grid,
            definitions_a=self.definitions_a,
            definitions_d=self.definitions_d
        )

    def _interpret_cword_data(self, 
                              crossword: cwg.Crossword
                              ) ->  None:
        '''Iterate through the range of the crosswords dimensions and gather data that will aid
        the templated html in the webapp to function properly.
        '''
        self.starting_word_positions: List[Tuple[int]] = list(crossword.data.keys()) # The keys are the position of the 
                                                                   # start of words
        '''example: [(1, 2), (4, 6)]'''
        
        self.definitions_a: List[Dict[int, Tuple[str]]] = list() 
        self.definitions_d = list()
        '''example: [{1: ("hello", "a standard english greeting)}]'''
        
        self.starting_word_matrix: List[List[int]] = deepcopy(crossword.grid)
        '''example: [[1, 0, 0, 0], 
                    [[0, 0, 2, 0]] 
           Each incremented number is the start of a new word.
        '''
        
        num_label = 1 # The key in `definitions_a` and `definitions_d`. Represents the start of a word 
                      # in the crossword grid with label in the top left of their cell. Since the 
                      # for loop in this function moves row by row, the number labels will gradually
                      # increase as you move down the crossword, making it easier to find a word
                      # when filling it in.
        for row in range(crossword.dimensions):
            for column in range(crossword.dimensions):
                if (row, column) in self.starting_word_positions:
                    current_cword_data = crossword.data[(row, column)]
                    if current_cword_data["direction"] == CrosswordDirections.ACROSS:
                        self.definitions_a.append({num_label: (current_cword_data["word"], 
                                                               current_cword_data["definition"])})
                    elif current_cword_data["direction"] == CrosswordDirections.DOWN:
                        self.definitions_d.append({num_label: (current_cword_data["word"], 
                                                               current_cword_data["definition"])})
                        
                    self.starting_word_matrix[row][column] = num_label
                    num_label += 1 # Only increment when a new word start was just found
                    
                else:   
                    self.starting_word_matrix[row][column] = 0 # No words starts here
    
    def _generate_crossword_category_blocks(self) -> None:
        self.category_block_objects: List[CrosswordCategoryBlock] = list()
        i = 0
        for category in [f for f in os.scandir(Paths.BASE_CWORDS_PATH) if f.is_dir()]:
            block = CrosswordCategoryBlock(self.horizontal_scroll_frame, self, category.name, i)
            block.pack(side="left", padx=5, pady=(5, 0))
            self.category_block_objects.append(block)
            i += 1
  
    def _on_cword_selection(self, 
                            name: str, 
                            word_count: int,
                            category: str,
                            category_object: object,
                            value: int
                            ) -> None:
        '''Called by an instance of `CrosswordInfoBlock`, which passes the data for its given crossword 
        into this method. The method then saves this data, deselects any previous word count radiobutton
        selections, reconfigures the values of the custom word count optionmenu to be compatible with
        the newly selected crossword, and reconfigures the max word count label to show the correct
        maximum word count.
        '''        
        if not self.cword_launch_options_enabled:
            self._configure_cword_launch_options_state("normal")
            self.cword_launch_options_enabled: bool = True

        self.b_load_selected_cword.configure(state="disabled")
        self.custom_word_count_optionmenu.configure(state="disabled")
        self.word_count_preference.set(-1)
        self.custom_word_count_optionmenu.set(_("Select word count"))
        
        # Always save the current crosswords name and word count to be ready for the user to laod it
        self.selected_cword_name: str = name
        self.selected_cword_word_count: int = word_count
        self.selected_cword_category: str = category
        self.selected_category_object: object = category_object
        
        self.custom_word_count_optionmenu.configure(values=[str(numbers.format_decimal(num, locale=self.master.locale))\
                                                           for num in range(3, word_count + 1)])
        self.radiobutton_max_word_count.configure(text=f"{_("Maximum")}: {numbers.format_decimal(word_count, locale=self.master.locale)}")
    
    def go_to_home(self) -> None:
        '''Removes the content of `CrosswordBrowser` and regenerates the `Home` classes content. This
        must be done outside of this class.
        '''
        if self.webapp_running:
            if AppHelper.confirm_with_messagebox(go_to_home=True):
                self.terminate_cword_webapp()
            else: 
                return
            
        self.master.close_cword_browser()


class CrosswordCategoryBlock(ctk.CTkFrame):
    '''A frame containing the name of a crossword category and a button to open all the crosswords
    contained within that category. Opening a category block will remove all other category blocks
    and display only the crosswords within that category (in the crossword browser panel).
    '''
    def __init__(self, 
                 container: ctk.CTkFrame, 
                 master: CrosswordBrowser, 
                 category: str,
                 value: int
                 ) -> None:
        super().__init__(container)
        self.configure(fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN), 
                       border_color=(Colour.Light.SUB, Colour.Dark.SUB), border_width=3, corner_radius=10)
        self.master = master
        self.category = category
        self.value = value

        self.selected_block = ctk.IntVar()
        self.selected_block.set(-1)

        self._make_content()
        self._place_content()
    
    def _make_content(self):
        self.category_name_textbox = ctk.CTkTextbox(self, font=self.master.master.CATEGORY_FONT,
                                                    wrap="word", fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
                                                    scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        self.category_name_textbox.tag_config("center", justify="center")
        self.category_name_textbox.insert("end", _(self.category.title()), "center")
        self.category_name_textbox.configure(state="disabled")
        
        self.b_view_category = ctk.CTkButton(self, font=self.master.master.TEXT_FONT, text=_("View"),
                                             command=self._view_category, width=65)
        self.b_close_category = ctk.CTkButton(self, font=self.master.master.TEXT_FONT, text=_("Close"),
                                              command=self._close_category, fg_color=Colour.Global.EXIT_BUTTON,
                                              hover_color=Colour.Global.EXIT_BUTTON_HOVER, width=65)
        self.bottom_colour_tag = ctk.CTkLabel(self, text="", fg_color=self._load_category_colour_tag(),
                                              corner_radius=10)
        
    def _place_content(self):
        self.category_name_textbox.place(relx=0.5, rely=0.2, anchor="c", relwidth=0.9, relheight=0.231)
        self.b_view_category.place(relx=0.5, rely=0.5, anchor="c")
        self.bottom_colour_tag.place(relx=0.5, rely=0.895, anchor="c", relwidth=0.75, relheight=0.06)

    def _load_category_colour_tag(self) -> str:
        with open(os.path.join(Paths.BASE_CWORDS_PATH, self.category, "info.json"), "r") as file:
            return json.load(file)["bottom_tag_colour"]
    
    def _sort_category_content(self,
                               arr: List[str]
                               ) -> List[str]:
        '''Sort the cword content of a category by the cword suffixes (-easy, to -extreme), if possible.'''
        try: 
            return sorted(arr, key=lambda i: CrosswordDifficulties.DIFFICULTIES.index(i.split("-")[-1].capitalize()))
        except: 
            return arr
    
    def _configure_cword_blocks_state(self, 
                                      state_: Union["disabled", "normal"]
                                      ) -> None:
        '''Toggle the crossword info block radiobutton (for selection) to either "disabled" or "normal".'''
        for block in self.cword_block_objects:
            block.radiobutton_selector.configure(state=state_) 
    
    def _view_category(self) -> None:
        '''View all crossword info blocks for a specific category.'''
        self.b_view_category.configure(state="disabled")
        for block in self.master.category_block_objects: # Remove all category blocks
            block.pack_forget()
        self.selected_block.set(-1)
        self.pack(side="left", padx=5, pady=(5, 0)) # Pack self (the selected category) back in
        
        # Create the blocks for the crosswords in the selected category
        self.cword_block_objects: List[CrosswordInfoBlock] = list() 
        i = 1
        for cword in self._sort_category_content([f.name for f in os.scandir(os.path.join(Paths.BASE_CWORDS_PATH, self.category)) if f.is_dir()]):
            block = CrosswordInfoBlock(self.master.horizontal_scroll_frame, self.master, cword, self.category, self, i)
            block.pack(side="left", padx=5, pady=(5, 0)) 
            self.cword_block_objects.append(block)
            i += 1
            
        self.b_close_category.place(relx=0.5, rely=0.7, anchor="c")
    
    def _close_category(self):
        '''Remove all crossword info blocks, and regenerate the category blocks.'''
        self.b_view_category.configure(state="normal")
        self.b_close_category.place_forget()
        for block in self.cword_block_objects:
            block.pack_forget()
        self.pack_forget()
        self.master._generate_crossword_category_blocks()
        self.master.b_load_selected_cword.configure(state="disabled")
        self.master.terminate_cword_webapp()
    

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
                 category: str,
                 category_object: CrosswordCategoryBlock,
                 value: int # Used for `self.radiobutton_selector`
                 ) -> None: 
        super().__init__(container)
        self.configure(fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN), 
                       border_color=(Colour.Light.SUB, Colour.Dark.SUB), border_width=3, 
                       corner_radius=10)
        self.master = master
        self.name = name
        self.category = category
        self.category_object = category_object
        self.value = value
        self.info = AppHelper._load_cword_info(self.category, self.name, self.master.master.locale.language)
        
        self._make_content()
        self._place_content()
        
    def _make_content(self) -> None:
        self.name_textbox = ctk.CTkTextbox(self, font=self.master.master.CWORD_BLOCK_FONT,
                                           wrap="word", fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
                                           scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        self.name_textbox.tag_config("center", justify="center")
        self.name_textbox.insert("end", f"{chr(int(self.info['symbol'], 16))} {self.info["translated_name"]}", "center")
        self.name_textbox.configure(state="disabled")

        self.l_total_words = ctk.CTkLabel(self, font=self.master.master.TEXT_FONT,
                                          text=f"{_("Total words")}: {numbers.format_decimal(self.info['total_definitions'], 
                                                                                            locale=self.master.master.locale)}")
        
        self.l_difficulty = ctk.CTkLabel(self, font=self.master.master.TEXT_FONT,
                    text=f"{_("Difficulty")}: {_(CrosswordDifficulties.DIFFICULTIES[self.info['difficulty']])}")
        
        self.bottom_colour_tag = ctk.CTkLabel(self, text="", fg_color=Colour.Global.DIFFICULTIES[self.info["difficulty"]],
                                              corner_radius=10)
        
        self.radiobutton_selector = ctk.CTkRadioButton(self, text=_("Select"), corner_radius=1,
                        font=self.master.master.TEXT_FONT,
                        variable=self.category_object.selected_block, 
                        value=self.value, 
                        # Pass the necessary info to `self.master._on_cword_selection` so it can
                        # appropriately configure the word count preferences for the user.
                        command=lambda name=self.name, word_count=self.info["total_definitions"], category=self.category, \
                        category_object=self.category_object, value=self.value: \
                            self.master._on_cword_selection(name, word_count, category, category_object, value))
    
    def _place_content(self) -> None:
        self.name_textbox.place(relx=0.5, rely=0.2, anchor="c", relwidth=0.9, relheight=0.198)
        self.l_total_words.place(relx=0.5, rely=0.47, anchor="c")
        self.l_difficulty.place(relx=0.5, rely=0.58, anchor="c")
        self.radiobutton_selector.place(relx=0.5, rely=0.76, anchor="c")
        self.bottom_colour_tag.place(relx=0.5, rely=0.9, anchor="c", relwidth=0.75, relheight=0.025)
        

class AppHelper:
    '''Miscellaneous functions that aid the other classes of `main.py`.'''
    @staticmethod
    def start_app() -> None:
        '''Initialise the cfg (config) object and the locale object, then instantiate the `Home`
        class with these objects and language information returned from `AppHelper._get_language_options`.
        '''
        cfg = ConfigParser()
        cfg.read(Paths.CONFIG_PATH)
        
        language: str = cfg.get("m", "language")
        locale: Locale = Locale.parse(language)
        gettext.translation("messages", localedir=Paths.LOCALES_PATH, languages=[locale.language]).install()
        AppHelper._update_config(cfg, "misc", "launches", str(int(cfg.get("misc", "launches")) + 1))
        
        app = Home(AppHelper._get_language_options(), locale, cfg)
        app.mainloop()
    
    @staticmethod
    def confirm_with_messagebox(exit_: bool = False, 
                                restart: bool = False,
                                go_to_home: bool = False
                                ) -> bool:
        if exit_ and restart:
            if tk.messagebox.askyesno(_("Restart"), _("Are you sure you want to restart the app?")):
                return True
        
        if exit_ and not restart:
            if tk.messagebox.askyesno(_("Exit"), 
                                      _("Are you sure you want to exit the app? If the web app is running, "
                                      "it will be terminated.")):
                return True
        
        if go_to_home:
            if tk.messagebox.askyesno(_("Back to home"), 
                                      _("Are you sure you want to go back to the home screen? The web "
                                      "app will be terminated.")):
                return True
        
        return False
    
    @staticmethod
    def show_messagebox(same_lang: bool = False, 
                        same_scale: bool = False, 
                        same_appearance: bool = False,
                        first_time_opening_cword_browser: bool = False
                        ) -> None:
        if same_lang:
            tk.messagebox.showerror(_("Error"), _("This language is already selected."))
        
        if same_scale:
            tk.messagebox.showerror(_("Error"), _("This size is already selected."))
        
        if same_appearance:
            tk.messagebox.showerror(_("Error"), _("This appearance is already selected."))
        
        if first_time_opening_cword_browser:
            tk.messagebox.showinfo(_("Info"), 
                _("First time launch, please read: Once you have loaded a crossword, and wish to load "
                "another one, you must first terminate the web app. IMPORTANT: If you are on macOS, "
                "force quitting the application (using cmd+q) while the web app is running will prevent "
                "it from properly terminating. If you mistakenly do this, either find the Flask app "
                "process and terminate it, change the `webapp_port` number in src/config.ini, or "
                "restart your computer. ALSO IMPORTANT: In some cases, you may have launched "
                "the web app yet your browser cannot view it. If this happens, please restart your browser."))
    
    @staticmethod
    def _update_config(cfg: ConfigParser, 
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
        localised_lang_db: Dict[str, str] = dict() # Used to retrieve the language code for the selected language
        ''' example:
        {"አማርኛ": "am",}
        '''
        
        localised_langs: Dict[str, str] = list() # Used in the language selection optionmenu
        ''' example:
        ["አማርኛ", "عربي"]
        '''
        
        locales = sorted(os.listdir(Paths.LOCALES_PATH))
        locales.remove("base.pot")
        i = 0
        for file_name in locales:
            if file_name.startswith("."): continue
            localised_langs.append(Locale.parse(file_name).language_name)
            localised_lang_db[localised_langs[i]] = file_name
            i += 1
        
        return [localised_lang_db, localised_langs]

    @staticmethod
    def _load_cword_info(category,
                         name: str, 
                         language: str = "en"
                         ) -> Dict[str, Union[str, int]]:
        '''Load the `info.json` file for a crossword. Called by an instance of `CrosswordInfoBlock`.'''
        with open(os.path.join(Paths.LOCALES_PATH, language, "cwords", category, name, "info.json"), "r") as file:
            info = json.load(file)
        
        return info
    
    @staticmethod
    def _get_colour_palette_for_webapp(appearance_mode: str) -> Dict[str, str]:
        '''Create a dictionary based on the `constants.Colour` for the web app.'''
        sub_class = Colour.Light if appearance_mode == "Light" else Colour.Dark
        palette = {key: value for attr in [sub_class.__dict__, Colour.Global.__dict__]
                  for key, value in attr.items() if key[0] != "_" or key.startswith("BUTTON")}
        return palette

    
if __name__ == "__main__":
    AppHelper.start_app()