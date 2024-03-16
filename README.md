![licence](https://img.shields.io/badge/licence-MIT-green?style=flat?logo=licence)
[![release)](https://img.shields.io/github/v/release/tomasvana10/crossword_puzzle?logo=github)](https://github.com/tomasvana10/crossword_puzzle/releases/latest)
[![issues](https://img.shields.io/github/issues-raw/tomasvana10/crossword_puzzle.svg?maxAge=25000)](https://github.com/tomasvana10/crossword_puzzle/issues)

# crossword_puzzle
A GUI application built with `CustomTkinter` that allows you to select, configure and generate a crossword to view, interact with and complete in a `Flask` web application.
- Download the latest version: [click here](https://github.com/tomasvana10/crossword_puzzle/releases/latest)
<br><br>
## Dependencies
`Babel==2.14.0`<br>
`customtkinter==5.2.2`<br>
`Flask==3.0.1`<br>
`flask_babel==4.0.0`<br>
`Pillow==10.2.0`<br>
`regex==2023.6.3`
<br><br>
## Installation
Requires [pip](https://pip.pypa.io/en/stable/installation/) and [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
1. `git clone https://github.com/tomasvana10/crossword_puzzle.git`
2. `cd crossword_puzzle`
3. Make a virtual environment with [virtualenv](https://virtualenv.pypa.io/en/latest/) (recommended)
   - `pip install virtualenv`
   - `python3 -m venv venv`
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python3 src/main.py` (if this doesn't work, try using `python` instead of `python3`)
<br><br>
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
<img width="683" alt="home page" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/38783814-148f-470f-b08a-aeea51e75a24">
<img width="872" alt="browser page" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/6b9705a1-e9ae-4505-8c48-e18ccbe7f586">
<img width="1240" alt="game english" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/6c313430-58df-4075-a417-b0150968be82">
<img width="1240" alt="game japanese" src="https://github.com/tomasvana10/crossword_puzzle/assets/124552709/92e84095-05ff-413f-b397-0c407e71d713">