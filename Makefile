# Constants
BABEL_CFG = xpuz/babel.cfg
LOCALES = xpuz/locales
BASE_POT = xpuz/locales/base.pot
TRANSLATOR = xpuz/__dev.py

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