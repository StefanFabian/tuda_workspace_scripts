#!/bin/sh

if _TMP_TARGET_DIR=$(_tuda_wss_get_workspace_root); then
  if [ $# -gt 0 ]; then
    # Unfortunately colcon doesn't return non-zero exit code if package name is not found but only prints a warning,
    # hence, we catch that.
    _TMP_COLCON_ERROR=$(colcon list --base-paths "$_TMP_TARGET_DIR" --packages-select $1 --paths-only 2>&1 >/dev/null)
    if [ ! -z "$_TMP_COLCON_ERROR" ]; then
      echo "[ERROR] Package '$1' not found." >&2
      return 1
    fi
    _TMP_TARGET_DIR=$(colcon list --base-paths "$_TMP_TARGET_DIR" --packages-select $1 --paths-only 2>/dev/null)
    unset _TMP_COLCON_ERROR
  fi
  cd "$_TMP_TARGET_DIR" || return
fi
unset _TMP_TARGET_DIR
