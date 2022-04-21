#!/bin/bash

function _tudawss_cd_complete() {
  # Only one argument possible
  if [ ${#COMP_WORDS[@]} -gt 3 ]; then
    return 0
  fi
  COMPREPLY=( $( compgen -W "$(colcon list --base-paths $(_tuda_wss_get_workspace_root) --names-only)" -- "$(_get_cword)" ) )
  return 0
}

add_tuda_wss_completion "cd" "_tudawss_cd_complete"
