#!/bin/bash
set -euo pipefail

python3 gen.py
python3 -m PyInstaller --onefile --noconfirm --clean \
    --hidden-import Crypto --hidden-import Crypto.Cipher.AES \
    --hidden-import Crypto.Util.Padding --hidden-import colorama \
    --name main src/main.py
