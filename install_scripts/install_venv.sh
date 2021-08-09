#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"/..

if [ -d $SCRIPT_DIR/venv ] ; then
    echo "venv directory already exists"
    exit 0
fi

echo "Installing Compta in $SCRIPT_DIR/venv..."
pythonscript=python3.9
if ! command -v $pythonscript ; then
    pythonscript=python3.8
    if ! command -v $pythonscript ; then
        echo "Needs python 3.8 or 3.9"
        exit 1
    fi
fi
if ! $pythonscript -m venv $SCRIPT_DIR/venv ; then
    echo "Trying to install $pythonscript-venv..."
    sudo apt-get install $pythonscript-venv
    if ! $pythonscript -m venv $SCRIPT_DIR/venv ; then
        echo "Failed to make the venv"
        if [ -d $SCRIPT_DIR/venv ] ; then
            rm -r $SCRIPT_DIR/venv
        fi
        exit 1
    fi
fi
echo "...venv created. Activating..."
if ! source $SCRIPT_DIR/venv/bin/activate ; then
    echo "Failed to activate the venv"
    if [ -d $SCRIPT_DIR/venv ] ; then
        rm -r $SCRIPT_DIR/venv
    fi
    exit 1
fi
pip install --upgrade pip
echo "...venv activated. Installing Compta..."
pip install -r $SCRIPT_DIR/requirements.txt
echo "...installed"