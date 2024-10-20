#!/bin/sh

# define some colors to use with echo -e
RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
LGRAY='\033[0;37m'
DGRAY='\033[1;30m'
LRED='\033[1;31m'
LGREEN='\033[1;32m'
YELLOW='\033[1;33m'
LBLUE='\033[1;34m'
LPURPLE='\033[1;35m'
LCYAN='\033[1;36m'
WHITE='\033[1;37m'
NOCOLOR='\033[0m'

_echoc() {
    if [ $# -lt 2 ]; then
      echo "echoc usage: _echoc <COLOR> <TEXT>"
      return
    fi

    echo -ne "${1}"
    shift
    echo -e "${*}${NOCOLOR}"
}

_echo_error() {
    _echoc $RED "$@"
}

_echo_warn() {
    _echoc $YELLOW "$@"
}

_echo_debug() {
    _echoc $GREEN "$@"
}

_echo_info() {
    _echoc $LGREEN "$@"
}

_echo_note() {
    _echoc $LBLUE "$@"
}