#!/bin/sh
for arg in "$@"; do
  if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
    $TUDA_WSS_BASE_SCRIPTS/_discovery.py "$@"
    return 0
  fi
done

$TUDA_WSS_BASE_SCRIPTS/_discovery.py "$@"

if [[ -f "/tmp/hector/discovery_client.xml" ]]; then
    echo "setting export"
    export FASTRTPS_DEFAULT_PROFILES_FILE="/tmp/hector/discovery_client.xml"
else
    unset FASTRTPS_DEFAULT_PROFILES_FILE
fi