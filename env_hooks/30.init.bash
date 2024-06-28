#!/bin/bash

if [ -z "$COLCON_HOME" ]; then
  export COLCON_HOME=$(_tuda_wss_get_workspace_root)/.tuda_workspace_scripts/colcon_config
fi
