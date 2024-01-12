import tkinter as tk 
import tkinter.messagebox
import gettext
from pathlib import Path
from configparser import ConfigParser

import customtkinter as ctk 

import cword_gen as cwg


class Paths:
    CONFIG_PATH = Path(__file__).resolve().parents[0] / "config.ini"


class Home(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Crossword Generator - Home")
        self.geometry("600x600")
        ctk.set_appearance_mode(cfg.get("m", "appearance"))
        ctk.set_default_color_theme(cfg.get("m", "theme"))
        ctk.set_widget_scaling(float(cfg.get("m", "scale")))
        
        self._make_content()
    
    def _make_content(self):
        main_frame = ctk.CTkFrame(self, fg_color="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)
        main_frame.grid_rowconfigure(0, weight=1)

        settings_frame = ctk.CTkFrame(main_frame, fg_color="red")
        settings_frame.grid(row=0, column=1, sticky="nsew")
        





if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read(Paths.CONFIG_PATH)
    
    app = Home()
    app.mainloop()
