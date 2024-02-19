![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green?style=flat)
[![VERSION](https://badge.fury.io/gh/tomasvana10%2Fcrossword_puzzle.svg)](https://github.com/tomasvana10/crossword_puzzle/releases/)
[![ISSUES](https://img.shields.io/github/issues-raw/tomasvana10/crossword_puzzle.svg?maxAge=25000)](https://github.com/tomasvana10/crossword_puzzle/issues)

# crossword_puzzle
A GUI application built with `CustomTkinter` that allows you to select, configure and generate a crossword to view, interact with and complete in a `Flask` web application.
- Download the latest version: [click here](https://github.com/tomasvana10/crossword_puzzle/releases/latest)
<br><br>
## Dependencies
`Babel==2.14.0`<br>
`customtkinter==5.2.2`<br>
`Flask==3.0.1`<br>
`Pillow==10.2.0`<br>
`regex==2023.6.3`
<br><br>
## Installation
1. `git clone https://github.com/tomasvana10/crossword_puzzle.git`
2. `cd cword_puzzle`
3. Make a virtual environment (recommended)
   - `pip install virtualenv`
   - `python3 -m venv venv`
   - Windows: `venv\Scripts\activate`, MacOS/Linux: `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python3 src/main.py`
<br><br>
## Usage
Will create external user documentation and add it to the repository eventually.
<br><br>
## Third-party library acknowledgements
- [Babel](https://babel.pocoo.org/en/latest/) - l10n functionality and management of message catalogues
- [flask-babel](https://python-babel.github.io/flask-babel/) - i18n integration for the Flask web application
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Creation of the main GUI
- [Google.Cloud.Translation.V2](https://cloud.google.com/dotnet/docs/reference/Google.Cloud.Translation.V2/latest) - Translation of locales 
- [Pillow](https://pillow.readthedocs.io/en/stable/) - Image processing services