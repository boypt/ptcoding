#!/bin/bash

VPNNAME=$1
NOTAG=$2


if [[ -z $VPNNAME ]]; then
    echo "$0 VPNNAME"
    exit 1
fi

if [[ ${NOTAG,,} != "notail" ]] && pgrep "openvpn" > /dev/null ; then
    echo "Kill Old VPN Process ... "
    sudo killall openvpn
    echo "Wait for their exit ..."
    sleep 2
fi

cd /etc/openvpn/$VPNNAME
CONF=$(ls *.conf)
CONFFILE=${CONF[0]}

sudo openvpn --config ${CONFFILE} --daemon

if [[ $(ip route show|wc -l) -lt 20 ]]; then
    echo "Add Route ... "
    sudo $(dirname $0)/vpn-route-add.sh
fi

if [[ ${NOTAG,,} != "notail" ]]; then
    tail -f /var/log/daemon.log
fi


