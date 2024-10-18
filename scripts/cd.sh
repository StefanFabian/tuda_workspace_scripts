#!/bin/sh

if _TMP_TARGET_DIR=$(_tuda_wss_get_workspace_root); then
  if [ $# -gt 0 ]; then
    _TMP_TARGET_DIR=$(python3 $TUDA_WSS_BASE_SCRIPTS/helpers/get_package_path.py $1)
    if [ -z "$_TMP_TARGET_DIR" ]; then
      echo "[ERROR] Package '$1' not found." >&2
      unset _TMP_TARGET_DIR
      return 1
    fi
  elif [ -d "$_TMP_TARGET_DIR/src" ]; then
    _TMP_TARGET_DIR="$_TMP_TARGET_DIR/src"
  fi
  cd "$_TMP_TARGET_DIR" || return
fi
unset _TMP_TARGET_DIR
