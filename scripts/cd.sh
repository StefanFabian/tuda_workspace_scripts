#!/bin/sh
_SCRIPT_DIR=$(dirname "$BASH_SOURCE[0]")
. "$_SCRIPT_DIR/helpers/output.sh"

if _TMP_TARGET_DIR=$(_tuda_wss_get_workspace_root); then
  if [ $# -gt 0 ]; then
    _TMP_TARGET_DIR=$(python3 $TUDA_WSS_BASE_SCRIPTS/helpers/get_package_path.py $1)
    if [ -z "$_TMP_TARGET_DIR" ]; then
      _echo_error "[ERROR] Package '$1' not found." >&2
      unset _TMP_TARGET_DIR
      return 1
    fi
  elif [ -d "$_TMP_TARGET_DIR/src" ]; then
    _TMP_TARGET_DIR="$_TMP_TARGET_DIR/src"
  fi
  cd "$_TMP_TARGET_DIR" || (unset _TMP_TARGET_DIR && return 1)
else
  _echo_error "No workspace configured." >&2
  _echo_info "Plese create a workspace, source it and mark the root folder containing src, build and install as a ros2 workspace using:"
  echo "tuda_wss init"
  return 1
fi
unset _TMP_TARGET_DIR
