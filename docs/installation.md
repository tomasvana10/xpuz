---
title: Installation
---

# Getting Started
Follow these steps to install and run `xpuz`, as well as the required dependencies.
???+ tip
    If using `pip` or `python` doesn't work, try using `pip3` or `python3`

## Installing Python and pip
- To install Python, download its installer [here](https://www.python.org/downloads/), or install it with [pyenv](https://github.com/pyenv/pyenv). Ensure you tick the box that says `Add Python 3 to PATH` in the installation wizard.
- If you have Python installed without pip, follow [this guide](https://pip.pypa.io/en/stable/installation/) to install it.

## Creating a virtual environment
It is strongly recommended that you create a virtual environment before installing `xpuz`. 

=== "Windows"

    ```powershell
    pip install virtualenv
    python -m venv myEnv
    myEnv\scripts\activate # (1)!
    ```

    1. If you cannot activate the virtual environment, try running `Set-ExecutionPolicy Unrestricted -Scope Process` in your terminal, ensuring you follow all the prompts. Then, try this step again.

=== "MacOS/Unix"

    ```sh
    pip install virtualenv
    python -m venv myEnv
    source myEnv/scripts/activate
    ```
    
???+ note
    Your virtual environment can be deactivated with the `deactivate` command.

## Installing `xpuz` and its optional dependencies
### with pip <small>recommended</small> { #with-pip data-toc-label="with pip" }
`xpuz` is published as [Python package](https://pypi.org/project/xpuz/) and can be installed with `pip`, ideally by using a [virtual environment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment). Open up your terminal (if you are unsure how, read [FAQ](faq.md)) and read the following instructions.

- Install `xpuz`
=== "Latest"

    ```sh
    pip install xpuz # (1)!
    ```

    1. You can add the `--user` flag to install `xpuz` in your home directory, which is useful if you aren't using a virtual environment.

=== "2.x.x"

    ```sh
    pip install xpuz=="2.*.*" 
    ```

- Install `tkinter` if you are on MacOS/Linux.
=== "MacOS"

    ```sh
    sudo pip install python3-tk
    ```

=== "Linux"

    ```sh
    sudo apt-get install python3-tk
    ```

- Install `pycairo` (optional)
```sh
pip install pycairo # (1)!
```

    1. `pycairo` is a feature dependency that is required if you want to make PDFs from your generated crosswords. If you are on an operating system other than Windows, please read [pycairo's Getting Started](https://pycairo.readthedocs.io/en/latest/getting_started.html) to install the required headers for `pycairo`.

        ???+ warning
            Languages whose alphabets use complex glyphs (such as Mandarin and Japanese) are not supported when making PDFs.

- Initialise the GUI.
```txt
xpuz-ctk
```

### with git { #with-git data-toc-label="with git" }
You can use the `git` version control system to clone the full repository and run `xpuz` directly with Python.
???+ note 
    You must install [git](https://git-scm.com/downloads) before using this method of installation.

```sh
git clone https://github.com/tomasvana10/xpuz.git
cd xpuz
pip install -r requirements.txt # (1)!
cd src
python -m xpuz
```

1. You can also install development dependencies by using `pip install -r devdeps.txt`. After you have done this and wish the build the project, ensure you are at the toplevel of the repository and run `python -m build` to build a wheel and tarball of the project.

## Updating
- Activate your virtual environment if you are using one.
   
- Update the package.
```
pip install -U xpuz
```

## Using Quickstart
You can utilise one of two scripts to quickly activate a virtual environment and update and start `xpuz`.

First, ensure you have [installed Python and pip](#installing-python-and-pip), then follow the OS specific steps.

=== "Windows"
    - Ensure you have script execution enabled. If you are unsure, run `Set-ExecutionPolicy Unrestricted -Scope Process` in your terminal and follow the prompts.
    - Download [quickstart-win.bat](https://github.com/tomasvana10/xpuz/blob/main/quickstart-win.bat).
    - Double click the script file or call it in command-line with `.\path\to\quickstart-win.bat`.

=== "MacOS/Unix"
      - Download [quickstart-posix.sh](https://github.com/tomasvana10/xpuz/blob/main/quickstart-posix.sh)
      - Call the script in the command-line with `source path/to/quickstart-posix.sh`.
