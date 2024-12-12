#!/bin/bash

if [[ -f "/tmp/hector/discovery_client.xml" ]]; then
    export FASTRTPS_DEFAULT_PROFILES_FILE="/tmp/hector/discovery_client.xml"
fi