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

arg1="${1:-}"
URL=$arg1

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
fi

if ! command -v curl >/dev/null; then
    red "curl required."
fi

if ! echo $URL | grep -q 'klouderr.com/download.php'; then
    red "$0 'klouderr.com/download.php?xxxxx' "
    exit 1
fi

UASTR='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
TEMPIMG=$(mktemp).png
TEMPCOOKIE=$(mktemp).jar
TEMPTORRENT=$(mktemp).torrent

torrent2magent () {
  green "6. Get torrent2magent (session init)"
  curl --silent --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent "${UASTR}" 'http://torrent2magnet.com/' -o /dev/null
  green "7. Upload torrent to get magent"
  curl --silent --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent "${UASTR}" --referer 'http://torrent2magnet.com/' -L -F"torrent_file=@$TEMPTORRENT;filename=1.torrent" 'http://torrent2magnet.com/upload/' | grep -Po '(?<=href=")(magnet:[^"]+)(?=")'
}


CAPTCHA=http://klouderr.com/captcha.php?rand=0.${RANDOM}${RANDOM}${RANDOM}
CURL="curl --silent --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent '"${UASTR}"' --referer $URL"

green "1.Get klouderr page($URL)"
eval "$CURL $URL -o /dev/null"

green "2.Get captcha img"
eval "$CURL $CAPTCHA -o $TEMPIMG"
cacaview "$TEMPIMG"
red_n "Enter Code:"
read CODE

green "3.Get torrent url, code:$CODE"
TORRENT=$(eval "$CURL -d 'downloadverify=1&d=1&captchacode='$CODE $URL" | grep -oE "http://.+?torrent" | head -n 1)

green "4.Wait 15"
line_sleep 15

green "5. Get torrent"
curl --silent -L -o "$TEMPTORRENT" "$TORRENT"

yellow $(file "$TEMPTORRENT" | grep "BitTorrent")
torrent2magent

rm -f $TEMPIMG $TEMPCOOKIE $TEMPTORRENT
