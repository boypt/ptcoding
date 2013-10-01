#!/bin/bash

function usage () {
    echo "Usage: $0 /path/to/openvpn/config.conf"
    echo
    echo "    then \`/path/to/openvpn/config-embed.conf' will be generated with [inline] data."
    exit 1
}

[ $# -eq 1 ] || usage
CONF=$(realpath $1)
[[ -f $CONF ]] || usage

CA=$(grep -e "^ca" $CONF|awk '{print $2}')
CERT=$(grep -e "^cert" $CONF|awk '{print $2}')
KEY=$(grep -e "^key" $CONF|awk '{print $2}')
TLS=$(grep -e "^tls-auth" $CONF|awk '{print $2}')

CONFBK=$(basename $CONF)
EMBED=${CONFBK%.*}-embed.conf
cd $(dirname $CONF)

cp $CONF $EMBED
if [[ ! -f $EMBED ]]; then
    echo "Can not write $EMBED, exit."
    exit 1;
fi

CONF=$EMBED
if [[ -r $CA ]]; then
    echo "Found CA file ... Replace with [inline]..."
    sed -i "s/^ca .\+/ca [inline]/" $CONF;
    (echo "<ca>"; cat $CA; echo "</ca>") >> $CONF
fi

if [[ -r $CERT ]]; then
    echo "Found CERT file ... Replace with [inline]..."
    sed -i "s/^cert .\+/cert [inline]/" $CONF;
    (echo "<cert>"; cat $CERT; echo "</cert>") >> $CONF
fi

if [[ -r $KEY ]]; then
    echo "Found KEY file ... Replace with [inline]..."
    sed -i "s/^key .\+/key [inline]/" $CONF;
    (echo "<key>"; cat $KEY; echo "</key>") >> $CONF
fi

if [[ -r $TLS ]]; then
    echo "Found TLS-AUTH file ... Replace with [inline]..."
    sed -i "s/^tls-auth \[^ \]\+/tls-auth  [inline]/" $CONF;
    (echo "<tls-auth>"; cat $TLS; echo "</tls-auth>") >> $CONF
fi

echo -e "\nDone. Here you go with only \`$(realpath $CONF)' "

