#!/bin/bash

#CAM1
CAMSSID_1="PIXPRO-SP360-4K_7B8B"
CAMPASS_1="password"
WLANINT_1="wlan1"
WLANIP_1="172.16.0.101"
WPAPID_1="/var/run/wpa1.pid"
WPALOG_1="/tmp/wpa1.log"

#CAM2
CAMSSID_2="PIXPRO-SP360-4K_7BAE"
CAMPASS_2="password"
WLANINT_2="wlan2"
WLANIP_2="172.16.0.102"
WPAPID_2="/var/run/wpa2.pid"
WPALOG_2="/tmp/wpa2.log"

ping_cam () {
    local SEQ=$1
    local WLANINT=$(eval echo \$WLANINT_$SEQ)
    ping -c 3 -I $WLANINT 172.16.0.254
}

connect_kodak () {
    local SEQ=$1
    local TABLEID=$((100+$SEQ))

    local CAMSSID=$(eval echo \$CAMSSID_$SEQ)
    local CAMPASS=$(eval echo \$CAMPASS_$SEQ)
    local WLANINT=$(eval echo \$WLANINT_$SEQ)
    local WLANIP=$(eval echo \$WLANIP_$SEQ)
    local WPAPID=$(eval echo \$WPAPID_$SEQ)
    local WPALOG=$(eval echo \$WPALOG_$SEQ)

    if [[ -e $WPAPID ]]; then
        kill $(cat $WPAPID)
    fi

    if ! iw dev $WLANINT info >/dev/null 2>&1; then
        echo "interface $WLANINT not found;"
        return 1
    fi

    ip link set up dev $WLANINT 

    # connect to AP in background
    wpa_supplicant -B -Dnl80211 \
        -P$WPAPID \
        -f$WPALOG \
        -i$WLANINT \
        -c<(wpa_passphrase $CAMSSID $CAMPASS)

    # flush ip / route 
    ip route flush table $TABLEID
    ip addr flush dev $WLANINT 
    ip rule del from $WLANIP lookup $TABLEID

    # add ip / route 
    ip addr add $WLANIP/24 dev $WLANINT 
    ip route del 172.16.0.0/24 dev $WLANINT table main
    ip route add 172.16.0.0/24 dev $WLANINT proto kernel scope link src $WLANIP table $TABLEID
    ip rule add from $WLANIP lookup $TABLEID
    ip route flush cache
}

connect_kodak 1 && ping_cam 1
connect_kodak 2 && ping_cam 2


