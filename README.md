![licence](https://img.shields.io/badge/licence-MIT-green?style=flat?logo=licence)
[![PyPI version](https://img.shields.io/pypi/v/crossword_puzzle?style=flat-square)](https://pypi.org/project/crossword_puzzle/)
[![Publish to PyPI.org](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/publish.yml/badge.svg)](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/publish.yml)
[![release)](https://img.shields.io/github/v/release/tomasvana10/crossword_puzzle?logo=github)](https://github.com/tomasvana10/crossword_puzzle/releases/latest)
[![issues](https://img.shields.io/github/issues-raw/tomasvana10/crossword_puzzle.svg?maxAge=25000)](https://github.com/tomasvana10/crossword_puzzle/issues)
[![CodeQL](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/github-code-scanning/codeql)
[![Tests](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/tox-tests.yml/badge.svg)](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/tox-tests.yml)

# crossword_puzzle
A GUI package built with `CustomTkinter` that allows you to select, configure and generate a crossword to view, interact with and complete in a `Flask` web application.
- Download the latest source code: [click here](https://github.com/tomasvana10/crossword_puzzle/releases/latest)
<br><br>
## Dependencies
`Babel==2.14.0`<br>
`customtkinter==5.2.2`<br>
`Flask==3.0.1`<br>
`flask_babel==4.0.0`<br>
`Pillow==10.2.0`<br>
`regex==2023.12.25`
<br><br>
## Installation
**Requires [pip](https://pip.pypa.io/en/stable/installation/)**

Make a virtual environment (recommended)
```
pip install virtualenv OR pip3 install virtualenv
python -m venv venv OR python3 -m venv venv
ON MACOS/UNIX: source venv/bin/activate
ON WINDOWS: venv\scripts\activate
```

Install the package in your system directory/virtual environment:
```
pip install -U crossword-puzzle OR pip3 install -U crossword-puzzle
```
OR, install the package in your home directory if you aren't using a virtual environment:
```
pip install --user -U crossword-puzzle
```
Then, run the GUI script:
```
crossword-ctk
```

## Documentation
Check out the wiki [here](https://github.com/tomasvana10/crossword_puzzle/wiki)
<br><br>
## Third-party library acknowledgements
- [CSS Pattern](https://css-pattern.com) - Background CSS patterns
- [Pure CSS Toggle Switch](https://codepen.io/morgoe/pen/VvzWQg) - Toggle switch CSS patterns
- [Zoomooz.js](https://jaukia.github.io/zoomooz/) - jQuery library for making webpage elements zoomable
- [Flask](https://flask.palletsprojects.com/en/3.0.x/) - Web framework for the crossword web application
- [Babel](https://babel.pocoo.org/en/latest/) - l10n functionality and management of message catalogues
- [flask-babel](https://python-babel.github.io/flask-babel/) - i18n integration for the Flask web application
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Creation of the main GUI
- [Google.Cloud.Translation.V2](https://cloud.google.com/dotnet/docs/reference/Google.Cloud.Translation.V2/latest) - Translation of locales 
- [Pillow](https://pillow.readthedocs.io/en/stable/) - Image processing services
- [regex](https://github.com/mrabarnett/mrab-regex) - Alternative to the standard `re` module, required for some functionality
<br><br>
## Gallery
![home](https://github.com/tomasvana10/crossword_puzzle/assets/124552709/b7472342-5cfe-418b-bdf1-cd7ab0389ace)
<hr>
![browser](https://github.com/tomasvana10/crossword_puzzle/assets/124552709/b3be1965-3847-45c8-99fd-b2ad284b46d9)
<hr>
![game-eng](https://github.com/tomasvana10/crossword_puzzle/assets/124552709/40c74282-8981-4b90-a29e-b4787d3ea134)
<hr>
![game-jp](https://github.com/tomasvana10/crossword_puzzle/assets/124552709/e892e74d-fa45-4866-8483-27b950cf152c)