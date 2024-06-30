<div align="center">
  
  # crossword_puzzle

</div>

<div align="center">

  <a href="">![cross-main-pic](https://github.com/tomasvana10/crossword_puzzle/assets/124552709/370a11cb-540e-41c4-8917-5f5272da2ebd)</a>
  <a href="">![licence](https://img.shields.io/badge/licence-MIT-green?style=flat?logo=licence)</a>
  <a href="">[![PyPI version](https://img.shields.io/pypi/v/crossword_puzzle?style=flat-square)](https://pypi.org/project/crossword_puzzle/)</a>
  <a href="">[![Publish to PyPI.org](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/publish.yml/badge.svg)](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/publish.yml)</a>
  <a href="">[![release](https://img.shields.io/github/v/release/tomasvana10/crossword_puzzle?logo=github)](https://github.com/tomasvana10/crossword_puzzle/releases/latest)</a>
  <a href="">[![issues](https://img.shields.io/github/issues-raw/tomasvana10/crossword_puzzle.svg?maxAge=25000)](https://github.com/tomasvana10/crossword_puzzle/issues)</a>
  <a href="">[![CodeQL](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/github-code-scanning/codeql)</a>
  <a href="">[![Tests](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/tox-tests.yml/badge.svg)](https://github.com/tomasvana10/crossword_puzzle/actions/workflows/tox-tests.yml)</a>
  
</div>

An educational GUI package built with `CustomTkinter` that allows you to design and play procedurally generated crosswords.
- Download the latest source code: [click here](https://github.com/tomasvana10/crossword_puzzle/releases/latest)

## Dependencies
`Babel`
`customtkinter`
`Flask`
`flask_babel`
`Pillow`
`regex`
`platformdirs`
`pathvalidate`
`CTkToolTip`

`pycairo` is an optional dependency that is required if you want to make PDFs from your generated crosswords. After reading **[Installation](#installation)** and installing the package, also run `pip install pycairo`. If you are on an operating system other than Windows, please also read **[pycairo's Getting Started](https://pycairo.readthedocs.io/en/latest/getting_started.html)** to install the required headers for `pycairo`.

> [!WARNING]  
> Languages whose alphabets use complex glyphs (such as Mandarin and Japanese) are not supported when making PDFs.

`pywebview` is another optional dependency that is required if you want to view crosswords in a webview instead of your browser. Please run `pip install pywebview` if this is the case.


## Tested python versions
- **Windows**: Python >= 3.7
- **MacOS**: Python >= 3.8
- **Linux**: Python >= 3.8

## Requirements
- **Hardware**
  - **RAM**: >120MB (GUI only), >500MB (GUI and browser to play crossword)
  - **CPU**: Any
  - **Storage**: >50MB available space

- **Software**
  - **OS**: Windows, MacOS, Linux
  - **Browser**: Not Internet Explorer
  - **Additional**: Python and pip (see **[Installation](#installation)**)

## Limitations
- Right-to-left scripts are not supported.
- Translations are made with a translation API, and therefore might be inaccurate.
- Crosswords may occasionally have one to two missing words.

## Installation
> [!IMPORTANT]
> Installing `crossword_puzzle` requires Python and pip.
> If you have Python installed without pip, click **[here](https://pip.pypa.io/en/stable/installation/)** to install it.<br><br>
> If you do not have Python installed, download the installer **[here](https://www.python.org/downloads/)**, or install it with **[pyenv](https://github.com/pyenv/pyenv)** (recommended). Then, refer to the previous link on how to install pip.<br><br>
> If you are on Linux or MacOS, you may not have Tkinter installed by default. Try running `sudo apt-get install python3-tk` on Linux or `sudo pip install python3-tk` on MacOS if this is the case.

> [!TIP]
> If using `python` or `pip` doesn't work, try using `python3` or `pip3`.

1. Make a virtual environment and activate it (recommended):
```
pip install virtualenv
python -m venv venv
MacOS/Unix: source venv/bin/activate
Windows: venv\scripts\activate
```
If you are on Windows and you cannot activate the virtual environment, try running `Set-ExecutionPolicy Unrestricted -Scope Process` and try again.
<br><br>

2. Install the package in your system directory/virtual environment:
```
pip install -U crossword-puzzle
```
or, install the package in your home directory if you aren't using a virtual environment:
```
pip install --user -U crossword-puzzle
```
<br>

3. Initialise the GUI through the entry point:
```
crossword-ctk
```
or, run the package manually through the terminal (requires [**Git**](https://git-scm.com/downloads)):
```
git clone https://github.com/tomasvana10/crossword_puzzle.git
cd crossword_puzzle
(make a virtual environment if you wish)
pip install -r requirements.txt
```
```py
python
>>> import crossword_puzzle as xp
>>> xp.main()
```
<br>

4. You can deactivate your virtual environment when you are done:
```
deactivate
```

## Documentation
Check out the wiki **[here](https://github.com/tomasvana10/crossword_puzzle/wiki)** for information on usage, troubleshooting, FAQ, and more.

## Third-party library acknowledgements
- [Flask](https://flask.palletsprojects.com/en/3.0.x/) - Web framework for the crossword web application
- [Babel](https://babel.pocoo.org/en/latest/) - l10n functionality and management of message catalogues
- [flask-babel](https://python-babel.github.io/flask-babel/) - i18n integration for the Flask web application
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Creation of the main GUI
- [platformdirs](https://pypi.org/project/platformdirs/) - Retrieving paths to platform-specific directories
- [Google.Cloud.Translation.V2](https://cloud.google.com/dotnet/docs/reference/Google.Cloud.Translation.V2/latest) - Translation of locales 
- [Pillow](https://pillow.readthedocs.io/en/stable/) - Image processing services
- [regex](https://github.com/mrabarnett/mrab-regex) - Alternative to the standard `re` module, required for some functionality
- [Zoomooz.js](https://jaukia.github.io/zoomooz/) - jQuery library for making webpage elements zoomable
- [gulp.js](https://gulpjs.com/) - Toolkit to help automate the web app's JavaScript transpilation
- [Babel.js](https://babeljs.io/) - JavaScript transpiler
- [Terser](https://terser.org/) - JavaScript minifier
- [CTkToolTip](https://github.com/Akascape/CTkToolTip) - Tooltips for forms in the crossword editor
- [pathvalidate](https://pypi.org/project/pathvalidate/) - Validating crossword name input
- [platformdirs](https://pypi.org/project/platformdirs/) - Storing config and user-made crosswords
- [Pycairo](https://pycairo.readthedocs.io/en/latest/) - Crossword PDF creation
- [pywebview](https://pywebview.flowrl.com/) - Browser webview to play crossword

## Other acknowledgements
- [NYTimes Mini Crossword](https://www.nytimes.com/crosswords/game/mini) - Heavily inspired the design of the web application
- [CSS Pattern](https://css-pattern.com) - Background CSS patterns
- [Pure CSS Toggle Switch](https://codepen.io/morgoe/pen/VvzWQg) - Toggle switch CSS patterns
- Crossword completion sound effect (CC attribution):
  - Jazzy Chords by NenadSimic -- https://freesound.org/s/150879/ -- License: Creative Commons 0

## Gallery
<img alt="crossword puzzle home" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/6b9eba14-220d-43dc-8b28-ddb92ea2d3b6">
<hr>
<img alt="crossword puzzle browser" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/6e5b7eae-970e-46b5-8a72-34d70bea2332">
<hr>
<img alt="crossword puzzle editor" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/33d7ec0c-ee2e-435f-9386-e7373f8a6378">
<hr>
<img alt="crossword puzzle game english" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/0475c6c4-e371-4d9d-837b-c06e0bde153f">
<hr>
<img alt="crossword puzzle game japanese" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/0e9d9d08-4a7c-4853-b83b-b2a27eab4b82">
