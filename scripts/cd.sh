#!/bin/sh
. "$TUDA_WSS_BASE_SCRIPTS/helpers/workspace.sh"

if TMP_WORKSPACE_PATH=$(_tuda_wss_get_workspace_root); then
  cd "$TMP_WORKSPACE_PATH" || return
fi
unset TMP_WORKSPACE_PATH
