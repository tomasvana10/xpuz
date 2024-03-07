'''Flask web app to produce an interactive interface to complete a crossword. The app is run when the
user presses the "Load crossword" button in the main GUI.
'''

import os
from multiprocessing import Process 
from pathlib import Path

from flask import Flask, render_template
from flask_babel import Babel

def _run(*args, **kwargs):
    '''Ran as a new Process using the `multiprocessing` module. kwargs are forwarded from
    `_create_app_process`, which forwards the arguments from `init_webapp` in `main.py`.
    '''
    app = Flask(__name__)
    app.config["BABEL_DEFAULT_LOCALE"] = kwargs["locale"].language
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = os.path.normpath(Path(__file__).resolve().parents[2] / "locales")
    babel = Babel(app)
    
    @app.route("/")
    def main():
        return render_template("index.html", **kwargs)
        
    app.run(debug=False, port=int(kwargs["port"]))
    

def _create_app_process(**kwargs):
    global server
    server = Process(target=_run, kwargs=kwargs)
    server.start()

def terminate_app():
    server.terminate()
    server.join()
