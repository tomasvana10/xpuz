## General troubleshooting
???+ question "The crossword game is too big or too small"
    - This is an issue on some browsers/computers. To fix it, simply press ++ctrl+plus++ or ++ctrl+minus++ (pressing ++cmd++ instead of ++ctrl++ if you are on MacOS) as many times as required to resize the game.

???+ question "`Zoom` doesn't work. Why?"
    - You likely did not have an active internet connection while opening the web app. This will prevent the `jquery` script from being fetched, thus removing the zoom plugin's functionality. 
    - Try connecting to the internet, reloading the crossword page (or loading a new crossword and opening it in a new tab), then try the the `Zoom` feature again.

???+ question "`pip`/`python` doesn't work when I type it into my terminal"
    - Ensure you are using the "right" `python`/`pip`, which may be `python3` or `pip3`.
    - Alternatively, read [installation](installation.md) to install `Python` or `pip` from scratch.

???+ question "I opened the web app and the crossword game did not appear"
    - You may have opened the web app without a browser open. Because of this, the browser may forget that it has to open a new tab with the crossword. Try pressing `Open` once more, or manually enter the address to the crossword game, which defaults to `localhost:5000`. The port may be different, if so, open the file at the path: `<documents-dir>/xpuz/config.ini` to see what your port is set to.

## Other issues
[Start a discussion](https://github.com/tomasvana10/xpuz/discussions/14){ .md-button }
[Open an issue](https://github.com/tomasvana10/xpuz/issues){ .md-button }