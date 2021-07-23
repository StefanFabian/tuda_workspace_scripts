#!/bin/sh

# @param directory: Directory from which to search the workspace root.
#   If not provided will try to find from current working directory and if that fails from the COLCON_PREFIX_PATH
# @return The path to the workspace root or None if no workspace found
_tuda_wss_get_workspace_root() {
  if [ $# -eq 1 ]; then
    if [ -f "$1/.ros2_workspace" ]; then
      echo "$1"
      return 0
    fi
    _TMP_PARENT=$(dirname "$1")
    if [ "$_TMP_PARENT" = "$1" ]; then
      unset _TMP_PARENT
      return 1
    fi
    if _tuda_wss_get_workspace_root "$_TMP_PARENT"; then
      unset _TMP_PARENT
      return 0
    fi
    unset _TMP_PARENT
    return 1
  fi
  # No dir passed, check current dir
  if _tuda_wss_get_workspace_root "$PWD"; then
    return 0
  fi
  # Not in current dir, check colcon prefix path
  if [ -n "$COLCON_PREFIX_PATH" ] && _tuda_wss_get_workspace_root "$COLCON_PREFIX_PATH"; then
    return 0
  fi
  return 1
}