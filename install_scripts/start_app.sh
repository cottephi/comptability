#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

venv_dir=$SCRIPT_DIR/../venv
activated=false

if ! [ -d $venv_dir ] ; then
    echo "Could not find a venv directory in Compta's directory. Creating one..."
    $SCRIPT_DIR/install_venv.sh
    activated=true
fi

if ! $activated ; then
    echo "Activating venv..."
    if ! source $venv_dir/bin/activate ; then
        echo "Failed to activate the venv"
        exit 1
    fi
fi
echo "Starting GUI..."
python $SCRIPT_DIR/../main_gui.py