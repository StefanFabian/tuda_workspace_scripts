#!/bin/bash

function _tudawss_cd_complete() {
  # Only one argument possible
  if [ ${#COMP_WORDS[@]} -gt 3 ]; then
    return 0
  fi
  COMPREPLY=( $( compgen -W "$(python3 $TUDA_WSS_BASE_SCRIPTS/helpers/get_package_names_in_workspace.py)" -- "$(_get_cword)" ) )
  return 0
}

add_tuda_wss_completion "cd" "_tudawss_cd_complete"
