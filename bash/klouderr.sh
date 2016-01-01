#!/bin/bash

URL=$1
if ! echo $URL | grep -q 'klouderr.com/download.php'; then
    echo "$0 'klouderr.com/download.php?xxxxx' "
    exit 1
fi

TEMPIMG=$(mktemp)
TEMPCOOKIE=$(mktemp)
CAPTCHA=http://klouderr.com/captcha.php?rand=0.${RANDOM}${RANDOM}${RANDOM}
CURL="curl -v --silent --cookie $TEMPCOOKIE --cookie-jar $TEMPCOOKIE --user-agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36' --referer $URL"
echo "Getting: $URL"

#http $URL  --session cap1  > /dev/null

eval "$CURL $URL" > /dev/null
#http $CAPTCHA Referer:$URL  --session cap1  > $TEMPIMG

eval "$CURL $CAPTCHA > $TEMPIMG"
mplayer -monitorpixelaspect 0.5 -nosub -contrast 25 -framedrop  -vo caca -quiet $TEMPIMG   2>/dev/null
echo -n "Enter Code:"
read CODE

#http $URL downloadverify=1 d=1 captchacode=$CODE  --session cap1 --form -p b | grep -oE "http://.+?torrent"
TORRENT=$(eval "$CURL -d 'downloadverify=1&d=1&captchacode='$CODE $URL" | grep -oE "http://.+?torrent" | head -n 1)

echo "-------------------------------------------"
echo "$TORRENT";
echo "-------------------------------------------"

#FILENAME=$(urldecode  $TORRENT | grep -oE '[^=]+?.torrent')
#echo "$CURL -o '/tmp/$FILENAME' '$TORRENT'"
#eval "$CURL -o '/tmp/$FILENAME' '$TORRENT'"
echo wget --content-disposition \'"$TORRENT"\'
wget --content-disposition "$TORRENT"

echo "Downloaded: $FILENAME"
rm $TEMPIMG $TEMPCOOKIE
