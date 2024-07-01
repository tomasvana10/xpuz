#!/bin/bash

cd ~

if [ ! -d venv]; then
    python3 -m venv venv || {
        python -m venv venv
    }
fi

source venv/bin/activate
pip3 install -U crossword-puzzle || {
    pip install -U crossword-puzzle
}
crossword-ctk
