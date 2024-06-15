"""Flask web app to produce an interactive interface to complete a crossword. 
The app is run when the user presses the "Load crossword" button in the main GUI.
"""

from configparser import ConfigParser
from logging import ERROR, getLogger
from multiprocessing import Process
from os import path
from socket import AF_INET, SOCK_STREAM, socket

from constants import CONFIG_PATH, LOCALES_PATH
from flask import Flask, render_template
from flask_babel import Babel
from utils import _update_config

app: Flask = Flask(__name__)
# Suppress info from Flask such as ``GET`` requests
logger = getLogger("werkzeug")
logger.setLevel(ERROR)
cfg: ConfigParser = ConfigParser()


def _app_process(*args, **kwargs) -> None:
    """Ran as a new Process using the ``multiprocessing`` module. Kwargs are
    forwarded from ``_create_app``, which forwards the arguments from
    ``main.init_webapp``.
    """

    @app.route("/")
    def index() -> str:
        return render_template("index.html", **kwargs)

    app.config["BABEL_DEFAULT_LOCALE"] = kwargs["locale"].language
    # Have to normalise the locales path because Flask cannot handle the
    # PosixPath object for some reason
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = path.normpath(LOCALES_PATH)
    babel: Babel = Babel(app)

    cfg.read(CONFIG_PATH)
    port = int(kwargs["port"])
    retry = False
    try:
        if not _is_port_in_use(port):
            app.run(debug=False, port=port)
        else:
            retry = True
    except Exception:  # Can be flask or socket related
        retry = True

    finally:
        if retry:
            print(f"\nPort {port} is not available, finding available port.")
            s: socket = socket()
            s.bind(("", 0))
            sock_name: int = s.getsockname()[1]
            _update_config(cfg, "misc", "webapp_port", str(sock_name))
            app.run(debug=False, port=sock_name)


def _is_port_in_use(port: int) -> bool:
    with socket(AF_INET, SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def _create_app(**kwargs) -> None:
    """Execute the ``_app_process`` function as a multithreaded process."""
    global server
    server = Process(target=_app_process, kwargs=kwargs)
    server.start()


def _terminate_app() -> None:
    if "server" in globals().keys():
        server.terminate()
        server.join()
