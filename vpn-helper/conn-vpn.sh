#!/bin/bash

VPNNAME=$1
NOTAG=$2

OLDVPNPID=$(pgrep openvpn)
if [[ ! -z $OLDVPNPID  && ${NOTAG,,} == "notail" ]]; then
    echo "Kill Old VPN Process ... "
    sudo kill -SIGTERM $OLDVPNPID
fi
echo "Wait for their exit ..."
sleep 2

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


