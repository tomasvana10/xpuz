"""Flask web app to produce an interactive interface to complete a crossword. 
The app is run when the user presses the "Load crossword" button in the main GUI.
"""

from configparser import ConfigParser
from multiprocessing import Process
from os import path
from socket import socket

from flask import Flask, render_template
from flask_babel import Babel

from crossword_puzzle.constants import Paths
from crossword_puzzle.utils import _update_config

app: Flask = Flask(__name__)
cfg: ConfigParser = ConfigParser()


def _server_process(*args, **kwargs) -> None:
    """Ran as a new Process using the ``multiprocessing`` module. Kwargs are
    forwarded from ``_create_app_process``, which forwards the arguments from
    ``main.init_webapp``.
    """

    @app.route("/")
    def index() -> str:
        return render_template("index.html", **kwargs)

    app.config["BABEL_DEFAULT_LOCALE"] = kwargs["locale"].language
    # Have to normalise the locales path because Flask cannot handle the
    # PosixPath object for some reason
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = path.normpath(
        Paths.LOCALES_PATH
    )
    babel: Babel = Babel(app)

    cfg.read(Paths.CONFIG_PATH)
    try:
        _update_config(cfg, "misc", "webapp_port", str(kwargs["port"]))
        app.run(debug=False, port=int(kwargs["port"]))
    except:  # Find an available port, since the current one is not available.
        print(
            f"\nPort {kwargs['port']} is not available, finding available "
            f"port..."
        )
        s: socket = socket()
        s.bind(("", 0))
        sock_name: int = s.getsockname()[1]
        _update_config(cfg, "misc", "webapp_port", str(sock_name))
        app.run(debug=False, port=sock_name)


def _create_app_process(**kwargs) -> None:
    """Execute the ``_server_process`` function as a multithreaded process."""
    global server
    server = Process(target=_server_process, kwargs=kwargs)
    server.start()


def terminate_app() -> None:
    if "server" in globals().keys():
        server.terminate()
        server.join()
