#!/bin/bash

URL=$1
if ! echo $URL | grep -q 'klouderr.com/download.php'; then
    echo "$0 'klouderr.com/download.php?xxxxx' "
    exit 1
fi

TEMPIMG=$(mktemp)
CAPTCHA=http://klouderr.com/captcha.php?rand=0.${RANDOM}${RANDOM}${RANDOM}
echo "Getting: $URL"

http $URL  --session cap1  > /dev/null
http $CAPTCHA Referer:$URL  --session cap1  > $TEMPIMG
mplayer  -monitorpixelaspect 0.5 -nosub -contrast 25 -framedrop  -vo caca -quiet $TEMPIMG   2>/dev/null
echo -n "Enter Code:"
read CODE
http $URL downloadverify=1 d=1 captchacode=$CODE  --session cap1 --form -p b | grep -oE "http://.+?torrent"

rm $TEMPIMG
