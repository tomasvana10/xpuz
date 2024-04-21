"""Flask web app to produce an interactive interface to complete a crossword. The app is run when the
user presses the "Load crossword" button in the main GUI.
"""

import os
from socket import socket
from configparser import ConfigParser
from multiprocessing import Process 
from pathlib import Path

from flask import Flask, render_template
from flask_babel import Babel

from crossword_puzzle.constants import Paths
app = Flask(__name__)
cfg = ConfigParser()

def _run(*args, **kwargs):
    """Ran as a new Process using the ``multiprocessing`` module. kwargs are 
    forwarded from ``_create_app_process``, which forwards the arguments from 
    ``init_webapp`` in ``main.py``.
    """
    @app.route("/")
    def main():
        return render_template("index.html", **kwargs)
    
    app.config["BABEL_DEFAULT_LOCALE"] = kwargs["locale"].language
    # Have to normalise the locales path because Flask cannot handle the 
    # PosixPath object for some reason
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = os.path.normpath(
                                                            Paths.LOCALES_PATH)
    babel = Babel(app)
    
    cfg.read(Paths.CONFIG_PATH)
    try:
        cfg["misc"]["webapp_port"] = str(kwargs["port"])
        _write_config()
        app.run(debug=False, port=int(kwargs["port"]))
    except: # Find an available port, since the current one is not available.
        print(f"\nPort {kwargs['port']} is not available, finding available "
              f"port...")
        s = socket()
        s.bind(("", 0))
        sock_name = s.getsockname()[1]
        cfg["misc"]["webapp_port"] = str(sock_name)
        _write_config()
        app.run(debug=False, port=sock_name)

def _write_config():
    with open(Paths.CONFIG_PATH, "w") as f:
        return cfg.write(f)

def _create_app_process(**kwargs):
    """Execute the ``_run`` function as a multithreaded process."""
    global server
    server = Process(target=_run, kwargs=kwargs)
    server.start()

def terminate_app():
    server.terminate()
    server.join()
