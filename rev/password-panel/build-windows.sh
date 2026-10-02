#!/bin/sh
set -eu

# Wine refuses a prefix owned by another user (the image default is root).
. /opt/mkuserwineprefix

xvfb-run sh -c "
  wine pip install --no-warn-script-location pycryptodome colorama
  wine python gen.py
  wine python -m PyInstaller --onefile --noconfirm --clean \
    --hidden-import Crypto --hidden-import Crypto.Cipher.AES \
    --hidden-import Crypto.Util.Padding --hidden-import colorama \
    --name main.exe --distpath dist --workpath /tmp/pyi-win --specpath /tmp src/main.py
  wineserver -w
"
