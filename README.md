<div align="center">
  
  # xpuz

</div>

<div align="center">

  ![crossword banner](https://github.com/tomasvana10/xpuz/assets/124552709/370a11cb-540e-41c4-8917-5f5272da2ebd)
  ![licence](https://img.shields.io/badge/licence-MIT-green?style=flat?logo=licence)
  [![PyPI version](https://img.shields.io/pypi/v/xpuz?style=flat-square)](https://pypi.org/project/xpuz/)
  [![Publish to PyPI.org](https://github.com/tomasvana10/xpuz/actions/workflows/publish.yml/badge.svg)](https://github.com/tomasvana10/xpuz/actions/workflows/publish.yml)
  [![release](https://img.shields.io/github/v/release/tomasvana10/xpuz?logo=github)](https://github.com/tomasvana10/xpuz/releases/latest)
  [![issues](https://img.shields.io/github/issues-raw/tomasvana10/xpuz.svg?maxAge=25000)](https://github.com/tomasvana10/xpuz/issues)
  [![CodeQL](https://github.com/tomasvana10/xpuz/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/tomasvana10/xpuz/actions/workflows/github-code-scanning/codeql)
  [![Tests](https://github.com/tomasvana10/xpuz/actions/workflows/tox-tests.yml/badge.svg)](https://github.com/tomasvana10/xpuz/actions/workflows/tox-tests.yml)
  
</div>

An educational GUI/web package built with `CustomTkinter` and `Flask` that allows you to design and play procedurally generated crosswords.
- Download the latest source code: [click here](https://github.com/tomasvana10/xpuz/releases/latest)

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

`pycairo` is an optional dependency that is required if you want to make PDFs from your generated crosswords. After reading [Installation](#installation) and installing the package, also run `pip install pycairo`. If you are on an operating system other than Windows, please also read [pycairo's Getting Started](https://pycairo.readthedocs.io/en/latest/getting_started.html) to install the required headers for `pycairo`.

> [!WARNING]  
> Languages whose alphabets use complex glyphs (such as Mandarin and Japanese) are not supported when making PDFs.

## Tested Python versions
- **Windows**: Python >= 3.7
- **MacOS**: Python >= 3.8
- **Linux**: Python >= 3.8

## Requirements
- **Hardware**
  - **RAM**: >120MB (GUI only), >500MB (GUI and browser to play crossword)
  - **CPU**: Any
  - **Storage**: >30MB available space (the program and its dependencies)

- **Software**
  - **OS**: Windows, MacOS, Linux
  - **Browser**: Not Internet Explorer
  - **Additional**: Python and pip (see [Installation](#installation))

## Limitations
- Right-to-left scripts are not supported.
- Translations are made with a translation API, and therefore might be inaccurate.
- Generated crosswords may occasionally have a few missing words.
- If your OS scaling is higher than the default, the web application will likely be too big. Read [Troubleshooting](https://github.com/tomasvana10/xpuz/wiki/Troubleshooting) for more information.

## Installation
> [!IMPORTANT]
> Installing `xpuz` requires Python3 and pip.
> If you have Python3 installed without pip, click [here](https://pip.pypa.io/en/stable/installation/) to install it.<br><br>
> If you do not have Python3 installed, download the installer [here](https://www.python.org/downloads/), or install it with [pyenv](https://github.com/pyenv/pyenv) (recommended). Then, refer to the previous link on how to install pip.<br><br>
> **Linux and MacOS users**: You may not have Tkinter installed by default. Try running `sudo apt-get install python3-tk` on Linux or `sudo pip install python3-tk` on MacOS if this is the case.

> [!TIP]
> If using `python` or `pip` doesn't work, try using `python3` or `pip3`.

1. Make a virtual environment and activate it (recommended):
```
pip install virtualenv
python -m venv venv
MacOS/Unix: source venv/bin/activate
Windows: venv\scripts\activate
```
**Windows users**: If you cannot activate the virtual environment, try running `Set-ExecutionPolicy Unrestricted -Scope Process` in your terminal, ensuring you follow all the prompts. Then, try this step again.

2. Install the package in your system directory/virtual environment:
```
pip install xpuz
```
or, install the package in your home directory if you aren't using a virtual environment:
```
pip install --user xpuz
```

3. Install pycairo if you want to make PDFs from your generated crosswords (read [Dependencies](#dependencies) for more information):
```
pip install pycairo
```

4. Initialise the GUI through the entry point:
```
xpuz-ctk
```
or, run the package manually through the terminal (requires [Git](https://git-scm.com/downloads)):
```
git clone https://github.com/tomasvana10/xpuz.git
cd xpuz
pip install -r requirements.txt
```
```py
>>> import xpuz as xp
>>> xp.main()
```

5. You can deactivate your virtual environment when you are done:
```
deactivate
```

## Updating
1. Activate your virtual environment if you are using one.
   
3. Update the package:
```
pip install -U xpuz
```

## Quickstart
You can utilise one of two scripts to quickly activate a virtual environment and update and start `xpuz`.

1. Read the `Important` section of [Installation](#installation) to install Python3 and pip
2. **Windows users**: Ensure you have script execution enabled. If you are unsure, run `Set-ExecutionPolicy Unrestricted -Scope Process` in your terminal and follow the prompts.
3. Download a quickstart file from the repository:
   - **Windows**: [quickstart-win.bat](https://github.com/tomasvana10/xpuz/blob/main/quickstart-win.bat)
   - **MacOS/Linux**: [quickstart-posix.sh](https://github.com/tomasvana10/xpuz/blob/main/quickstart-posix.sh)
4. Run the script:
   - **Windows**: Double click the script file or call it in command-line with `.\path\to\quickstart-win.bat`.
   - **MacOS/Linux**: Call the script in the command-line with `source path/to/quickstart-posix.sh`.

## Documentation
Check out the wiki [here](https://github.com/tomasvana10/xpuz/wiki) for information on usage, troubleshooting, FAQ, and more.

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
- Jazzy Chords by NenadSimic -- https://freesound.org/s/150879/ -- License: Creative Commons 0

## Gallery
<img alt="crossword puzzle home" src="https://github.com/tomasvana10/xpuz/assets/124552709/6b9eba14-220d-43dc-8b28-ddb92ea2d3b6">
<hr>
<img alt="crossword puzzle browser" src="https://github.com/tomasvana10/xpuz/assets/124552709/6e5b7eae-970e-46b5-8a72-34d70bea2332">
<hr>
<img alt="crossword puzzle editor" src="https://github.com/tomasvana10/xpuz/assets/124552709/33d7ec0c-ee2e-435f-9386-e7373f8a6378">
<hr>
<img alt="crossword puzzle game english" src="https://github.com/tomasvana10/xpuz/assets/124552709/0475c6c4-e371-4d9d-837b-c06e0bde153f">
<hr>
<img alt="crossword puzzle game japanese" src="https://github.com/tomasvana10/xpuz/assets/124552709/0e9d9d08-4a7c-4853-b83b-b2a27eab4b82">
