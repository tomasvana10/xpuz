from json import dump, load
from tkinter import filedialog
from os import mkdir, path, rmdir

from customtkinter import CTkLabel
from platformdirs import user_downloads_dir

from crossword_puzzle.td import CrosswordInfo


class Export(list):
    def __init__(self, blocks):
        self.blocks = blocks
        self.exported = False
        
        self._assemble()
        self._export()

    def _get_filepath(self):
        return filedialog.asksaveasfilename(
            title=_("Select a destination to export your crosswords to"),
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir=user_downloads_dir(),
            initialfile=_("my-crosswords") + ".json"
        )

    def _export(self) -> None:
        filepath = self._get_filepath()
        
        if not filepath:
            return 
        
        if not filepath.endswith(".json"):
            filepath += ".json"
        try:
            with open(filepath, "w") as f:
                dump(self, f, indent=4)
        except Exception:
            return
        
        self.exported = True
            
    def _assemble(self) -> None:
        for block in self.blocks:
            cwrapper = block.cwrapper
            self.append([cwrapper.fullname, {"info": cwrapper.info, "definitions": cwrapper.definitions}])

class Import:
    def __init__(self, master, fp):
        self.master = master
        self.fp = fp
        
        self.conflicting_fullnames = []
        self.skipped_crossword_fullnames = []
        self.imported_crossword_fullnames = []
        self.imported = False
        self.invalid_file = False
        
        self._import()
    
    def _get_filepath(self):
        return filedialog.askopenfilename(
            title=_("Select a valid crossword JSON file that was exported using crossword_puzzle"),
            initialdir=user_downloads_dir(),
            filetypes=[("JSON Files", "*.json")]
        )
    
    def _import(self):
        filepath = self._get_filepath()
    
        if not filepath:
            self.invalid_file = True
            return
    
        with open(filepath) as f:
            try:
                data = load(f)
            except Exception:
                self.invalid_file = True
                return
        
        if not isinstance(data, list):
            self.invalid_file = True
            return
    
        self._write(data)
        
    def _write(self, data):
        for crossword in data:
            if not isinstance(crossword, list) or len(crossword) != 2:
                self.invalid_file = True
                return
            
            name = crossword[0]
            crossword_data = crossword[1]
            toplevel = path.join(self.fp, name)
            try:
                mkdir(toplevel)
            except FileExistsError:
                self.conflicting_fullnames.append(name)
                continue
            
            try:
                info = crossword_data["info"]
                definitions = crossword_data["definitions"]
                if not all(
                    key in info for key in CrosswordInfo.__dict__["__annotations__"]
                ):
                    self.skipped_crossword_fullnames.append(name)
                    rmdir(toplevel)
                    continue
                
                self.master.master._write_data(toplevel, info, "info")
                self.master.master._write_data(toplevel, definitions, "definitions")
            except Exception:
                self.skipped_crossword_fullnames.append(name)
                continue
            
            self.imported_crossword_fullnames.append(name)
        
        self.imported = True
