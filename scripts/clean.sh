#!/bin/sh

TMP_REMOVAL_EXPORT=$($TUDA_WSS_BASE_SCRIPTS/helpers/remove_packages_from_env.py "$@")
if $TUDA_WSS_BASE_SCRIPTS/_clean.py "$@"; then
  eval "$TMP_REMOVAL_EXPORT"
fi
unset TMP_REMOVAL_EXPORT
