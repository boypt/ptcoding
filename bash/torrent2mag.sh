#!/usr/bin/env bash
# Bash3 Boilerplate. Copyright (c) 2014, kvz.io

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

# Set magic variables for current file & dir
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename ${__file} .sh)"
__root="$(cd "$(dirname "${__dir}")" && pwd)" # <-- change this as it depends on your app


black() { echo -e "$(tput setaf 0)$*$(tput setaf 9)"; }
red() { echo -e "$(tput setaf 1)$*$(tput setaf 9)"; }
green() { echo -e "$(tput setaf 2)$*$(tput setaf 9)"; }
yellow() { echo -e "$(tput setaf 3)$*$(tput setaf 9)"; }
blue() { echo -e "$(tput setaf 4)$*$(tput setaf 9)"; }
magenta() { echo -e "$(tput setaf 5)$*$(tput setaf 9)"; }
cyan() { echo -e "$(tput setaf 6)$*$(tput setaf 9)"; }
white() { echo -e "$(tput setaf 7)$*$(tput setaf 9)"; }

red_n() { echo -ne "$(tput setaf 1)$*$(tput setaf 9)"; }
cyan_n() { echo -ne "$(tput setaf 6)$*$(tput setaf 9)"; }
line_sleep () {
    local SEC=$1
    while [[ $SEC -gt 0 ]]; do
      printf -v P "%02d" $SEC
      cyan_n "-${P}-"
      SEC=$(($SEC-1))
      sleep 1
    done
    echo ""
}


if ! command -v cacaview >/dev/null; then
    red "caca-utils required."
    exit 1
fi

if ! command -v curl >/dev/null; then
    red "curl required."
    exit 1
fi

UASTR='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
TEMPCOOKIE=$(mktemp).jar

green ".Get torrent2magent (session init)"
CURL="curl --silent --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent '${UASTR}'"
eval "$CURL -o /dev/null http://torrent2magnet.com/"

torrent2mag () {
  local TEMPTORRENT=$1
  eval "$CURL --referer 'http://torrent2magnet.com/' -L -F\"torrent_file=@$TEMPTORRENT;filename=1.torrent\" 'http://torrent2magnet.com/upload/'" | grep -Po '(?<=href=")(magnet:[^"]+)(?=")'
}

for T in "$@"; do
  torrent2mag "$T"
done

rm -f $TEMPCOOKIE 

