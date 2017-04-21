#!/usr/bin/env bash
# Bash3 Boilerplate. Copyright (c) 2014, kvz.io

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

NGROK_CLIENT=http://wxdev.doctorcom.com/ngrok/ngrok-$(uname -m).tar.gz
NGROK_SERVER=wx.ptsang.net:44443
NGROK_TOKEN=

PORT="${1:-}"
setconfig () {
    local CONFIG=$1
    if ! echo $PORT | grep -q -E "^5[0-9]{4}$"; then
        while true; do
            echo "Enter mapping port number: (must be greater than 50000)"

            if ! tty --silent; then
                read PORT < /dev/tty
            else
                read PORT
            fi

            if echo $PORT | grep -q -E "^5[0-9]{4}$"; then
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

    echo "Mapping remote port $PORT"

    cat > $CONFIG << EOF
server_addr: "$NGROK_SERVER"
auth_token: "$NGROK_TOKEN"
tunnels:
    ssh:
        remote_port: $PORT
        proto:
            tcp: ":22"
EOF
    echo "---------------------"
}


if command -v curl > /dev/null 2>&1; then
    DOWNLOAD="$(which curl) -O"
elif command -v wget > /dev/null 2>&1; then
    DOWNLOAD="$(which wget)"
else
    echo "wget or curl not exists."
    exit 1
fi


NGROK_CLIENT_TAR=$(basename $NGROK_CLIENT)
cd /tmp

$DOWNLOAD ${NGROK_CLIENT}.md5
if ! md5sum -c $(basename ${NGROK_CLIENT}.md5); then
    $DOWNLOAD $NGROK_CLIENT
    md5sum -c $(basename ${NGROK_CLIENT}.md5)
fi


setconfig /tmp/ngrok.yml
if [[ $(id -u) == 0 ]]; then
  #is root
  tar xfz /tmp/$NGROK_CLIENT_TAR -C /usr/local/bin/
  install -v -m644 /tmp/ngrok.yml /etc/ngrok.yml
  sed -i -e '$i \ngrok -log=stdout -config=/etc/ngrok.yml start ssh >/dev/null 2>&1 &\n' /etc/rc.local
  echo "ngrok installed as root at /usr/local/bin/ngrok"
  echo "Config: /etc/ngrok.yml "
  echo "Autorun ngrok configured at /etc/rc.local"
  ngrok -log=stdout -config=/etc/ngrok.yml start ssh >/dev/null 2>&1 &
else
  tar xvfz /tmp/$NGROK_CLIENT_TAR -C ~
  install -v -m644  /tmp/ngrok.yml ~/.ngrok
  echo "ngrok installed at $HOME/ngrok"
  echo "Config: $HOME/.ngrok"
  echo "RUN: "
  echo "~/ngrok start ssh"
fi
rm -f /tmp/ngrok.yml

echo "---------------------"
echo "Done"
