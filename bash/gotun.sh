#!/usr/bin/env bash
# Bash3 Boilerplate. Copyright (c) 2014, kvz.io
# Map ssh tun to our ngrokd server

set -o errexit
#set -o pipefail
set -o nounset
# set -o xtrace

NGROK_CLIENT=http://wxdev.doctorcom.com/ngrok/ngrok.$(uname -m).tar.gz
NGROK_SERVER=wxdev.doctorcom.com
NGROK_PORT=50000
NGROK_TOKEN=
NGROK_BIN=ngrok
LOCAL_PORT="${1:-}"

if [ $(id -u) -eq 0 ]; then
  NGROK_EXEC=/usr/local/bin/ngrok
else
  NGROK_EXEC=/tmp/ngrok
fi

readconfig () {
    if ! echo $LOCAL_PORT | grep -q -E "^5[0-9]{4}$"; then
        while true; do
            echo "Enter mapping port number: (must be greater than 50000)"

            if ! tty --silent; then
                read LOCAL_PORT < /dev/tty
            else
                read LOCAL_PORT
            fi

            if echo $LOCAL_PORT | grep -q -E "^5[0-9]{4}$"; then
                break;
            fi
        done
    fi

    echo "Enter ServerToken"
    if ! tty --silent; then
        read NGROK_TOKEN < /dev/tty
    else
        read NGROK_TOKEN
    fi
}


if command -v curl > /dev/null 2>&1; then
    DOWNLOAD="$(which curl) -O"
elif command -v wget > /dev/null 2>&1; then
    DOWNLOAD="$(which wget)"
else
    echo "wget or curl not exists."
    exit 1
fi

readconfig 
NGROK_CLIENT_TAR=$(basename $NGROK_CLIENT)
TMPDIR=$(mktemp -d --suffix=ngrok-c)
cd $TMPDIR
$DOWNLOAD ${NGROK_CLIENT}
tar xfz $NGROK_CLIENT_TAR -C .

install -v -m755 ./$NGROK_BIN $NGROK_EXEC
cd /tmp
rm -rf $TMPDIR

CMD="$NGROK_EXEC -serveraddr=$NGROK_SERVER:$NGROK_PORT -authtoken=$NGROK_TOKEN -log=stdout -log-level=INFO -proto=tcp 22 $LOCAL_PORT"
echo '-------------------'
echo '----Run command----'
echo $CMD
echo '-------------------'
$CMD

