#!/bin/sh

TMP_REMOVAL_EXPORT=$(cd $TUDA_WSS_BASE_SCRIPTS >/dev/null 2>&1 || return 1; python3 -m helpers.remove_packages_from_env "$@")
if $TUDA_WSS_BASE_SCRIPTS/_clean.py "$@"; then
  eval "$TMP_REMOVAL_EXPORT"
fi
unset TMP_REMOVAL_EXPORT
