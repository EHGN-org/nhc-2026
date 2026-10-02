#!/bin/bash
set -e

CWD="$(cd "$(dirname "$0")" && pwd)"
NAME="$(basename "$CWD")"
cd "$CWD"

rm -rf "${NAME}_handout.zip"

tmp="$(mktemp -d)"
dir="$tmp/$NAME"
mkdir "$dir"
cp -r app.py docker-compose.yml Dockerfile entrypoint.sh readflag.c templates "$dir"

sed -i 's/#define FLAG .*/#define FLAG "CTF{f4k3_fl4g_f0r_t3st1ng}"/' "$dir/readflag.c"

cd "$tmp"
zip -r "$CWD/${NAME}_handout.zip" "$NAME"

rm -r "$tmp"
cd "$CWD"

echo "Release files created:"
ls -lh "${NAME}_handout.zip"
