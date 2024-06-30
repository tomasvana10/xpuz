# Constants
BABEL_CFG = crossword_puzzle/babel.cfg
LOCALES = crossword_puzzle/locales
BASE_POT = crossword_puzzle/locales/base.pot
TRANSLATOR = crossword_puzzle/__dev.py

# i18n
i18n: extract update translate compile

# init: pybabel init -l <locale> -i $(BASE_POT) -d $(LOCALES)

extract:
	pybabel extract -F $(BABEL_CFG) -o $(BASE_POT) .

update:
	pybabel update -i $(BASE_POT) -d $(LOCALES)

translate:
	python $(TRANSLATOR)

compile:
	pybabel compile -d $(LOCALES)