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

# allow command fail:
# fail_command || true


URL=$1
if ! echo $URL | grep -q 'klouderr.com/download.php'; then
    echo "$0 'klouderr.com/download.php?xxxxx' "
    exit 1
fi

UASTR='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
TEMPIMG=$(mktemp).png
TEMPCOOKIE=$(mktemp)
TEMPTORRENT=$(mktemp).torrent

torrent2magent () {
  curl --silent --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent "${UASTR}" 'http://torrent2magnet.com/' -o /dev/null
  echo '----------------------------------------------------------------------------'
  echo '----------------------------------------------------------------------------'
  echo '----------------------------------------------------------------------------'
  echo '----------------------------------------------------------------------------'
  curl --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent "${UASTR}" --referer 'http://torrent2magnet.com/' -L -F"torrent_file=@$TEMPTORRENT;filename=1.torrent" 'http://torrent2magnet.com/upload/' | grep -Po '(?<=href=")(magnet:[^"]+)(?=")'
}


CAPTCHA=http://klouderr.com/captcha.php?rand=0.${RANDOM}${RANDOM}${RANDOM}
CURL="curl --silent --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent '"${UASTR}"' --referer $URL"

#echo $CURL
echo "Getting: $URL"

#http $URL  --session cap1  > /dev/null

eval "$CURL $URL -o /dev/null"
#http $CAPTCHA Referer:$URL  --session cap1  > $TEMPIMG

eval "$CURL $CAPTCHA -o $TEMPIMG"
#mplayer -monitorpixelaspect 0.5 -nosub -contrast 25 -framedrop  -vo caca -quiet $TEMPIMG   2>/dev/null
feh $TEMPIMG || true
echo -n "Enter Code:"
read CODE

#http $URL downloadverify=1 d=1 captchacode=$CODE  --session cap1 --form -p b | grep -oE "http://.+?torrent"
#echo TORRENT=$(eval "$CURL -d 'downloadverify=1&d=1&captchacode='$CODE $URL" | grep -oE "http://.+?torrent" | head -n 1)

TORRENT=$(eval "$CURL -d 'downloadverify=1&d=1&captchacode='$CODE $URL" | grep -oE "http://.+?torrent" | head -n 1)

echo "-------------------------------------------"
echo "$TORRENT";
echo "-------------------------------------------"

#FILENAME=$(urldecode  $TORRENT | grep -oE '[^=]+?.torrent')
#echo "$CURL -o '/tmp/$FILENAME' '$TORRENT'"
#eval "$CURL -o '/tmp/$FILENAME' '$TORRENT'"
echo "wait 15"
sleep 15
#echo wget --content-disposition \'"$TORRENT"\'
#wget --content-disposition "$TORRENT"
curl -Lv -o "$TEMPTORRENT" "$TORRENT"
file "$TEMPTORRENT" 
torrent2magent

#echo "Downloaded: $FILENAME"
rm -f $TEMPIMG $TEMPCOOKIE
