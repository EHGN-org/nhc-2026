#!/bin/sh
set -e
GOCACHE="${GOCACHE:-/tmp/gocache}"
GOPATH="${GOPATH:-/tmp/gopath}"
mkdir -p "$GOCACHE" "$GOPATH/pkg/mod"
if [ -d /opt/gocache-seed ]; then
  cp -a /opt/gocache-seed/. "$GOCACHE/"
fi
exec python3 -m gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 4 --timeout 30 app:app
