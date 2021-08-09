#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

desktop=$HOME/Desktop

if ! [ -d $desktop ] ; then
  desktop=$HOME/Bureau
fi
if ! [ -d $desktop ] ; then
  desktop=$HOME
  echo "No desktop path found. Will create launcher in $desktop"
fi

git config core.fileMode false
chmod +x $SCRIPT_DIR/*.sh
$SCRIPT_DIR/install_venv.sh
echo "[Desktop Entry]
Name=compta
Comment=compta
Terminal=true
Exec=gnome-terminal -e \"bash -c '"$SCRIPT_DIR"/start_app.sh'\"
Type=Application
Icon=$SCRIPT_DIR/euro.png" > $desktop/compta.desktop
chmod +x $desktop/compta.desktop