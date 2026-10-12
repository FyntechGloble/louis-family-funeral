#!/bin/sh
set -eu
# Named Docker volumes can retain root ownership across deploys.
# Repair database directory ownership before dropping privileges.
chown -R appuser:appuser /data
exec gosu appuser "$@"
