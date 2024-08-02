"""Flask web app that produces an interactive interface to complete a crossword."""

from typing import Any, Dict
from configparser import ConfigParser
from logging import ERROR, getLogger
from multiprocessing import Process
from os import path
from socket import AF_INET, SOCK_STREAM, socket

from flask import Flask, render_template
from flask_babel import Babel

from xpuz.constants import LOCALES_PATH
from xpuz.utils import _read_cfg, _update_cfg

app: Flask = Flask(__name__)
# Suppress info from Flask such as ``GET`` requests
logger = getLogger("werkzeug")
logger.setLevel(ERROR)
cfg: ConfigParser = ConfigParser()


def _app_process(**kwargs: Dict[str, Any]) -> None:
    """This function is executed as a new Process with the `multiprocessing`
    module to ensure the web application does not block the execution of the 
    Tkinter GUI.
    
    Args:
        **kwargs: Jinja2 template and crossword-related data.
    """

    @app.route("/")
    def index() -> str:
        return render_template("index.html", **kwargs)

    app.config["BABEL_DEFAULT_LOCALE"] = kwargs["locale"].language
    # Have to normalise the locales path because Flask cannot handle the
    # PosixPath object for some reason
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = path.normpath(LOCALES_PATH)
    babel: Babel = Babel(app)

    _read_cfg(cfg)
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
            _update_cfg(cfg, "misc", "webapp_port", str(sock_name))
            app.run(debug=False, port=sock_name)


def _is_port_in_use(port: int) -> bool:
    """Check if `port` is in use.
    
    Args:
        port: The port to check
    
    Returns:
        Whether the port is in use or not.
    """
    with socket(AF_INET, SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def _create_app(**kwargs: Dict[str, Any]) -> None:
    """Execute the ``_app_process`` function as a multithreaded process.
    
    Args:
        **kwargs: Jinja2 template and crossword-related data.
    """
    global server
    server = Process(target=_app_process, kwargs=kwargs)
    server.start()


def _terminate_app() -> None:
    """Terminate the app process."""
    if "server" in globals().keys():
        server.terminate()
        server.join()
