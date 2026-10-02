#!/bin/bash
set -euo pipefail

CWD="$(cd "$(dirname "$0")" && pwd)"
NAME="$(basename "$CWD")"
cd "$CWD"

if [[ ! -f dist/main.exe || ! -f dist/main ]]; then
    echo "dist/main.exe or dist/main missing; run ./build.sh first" >&2
    exit 1
fi

rm -rf "${NAME}_handout.zip"

tmp="$(mktemp -d)"
dir="$tmp/$NAME"
mkdir "$dir"
cp dist/main.exe dist/main "$dir/"

cd "$tmp"
zip -r "$CWD/${NAME}_handout.zip" "$NAME"

rm -r "$tmp"
cd "$CWD"

echo "Release files created:"
ls -lh "${NAME}_handout.zip"
