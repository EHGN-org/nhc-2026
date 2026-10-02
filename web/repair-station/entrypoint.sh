#!/bin/sh
set -e

# Written at startup from FLAG so each instanced team gets its own value.
# Mode 0644: the intended RCE is as appuser (see Dockerfile USER), who must
# be able to `cat /flag.txt`.
FLAG_PATH="${FLAG_PATH:-/flag.txt}"
if [ -z "${FLAG}" ]; then
    FLAG='NHC{flag_env_var_not_set}'
fi
printf '%s\n' "${FLAG}" > "${FLAG_PATH}"
chmod 0644 "${FLAG_PATH}"

exec "$@"
