#!/usr/bin/env sh

#
# Cloudflare API Dynamic AAAA DNS Updater for IPv6 addresse in Bash
#
# Credit:
#   Part of this script got inspired from the work of `benkulbertis`@github:
#   https://gist.github.com/benkulbertis/fff10759c2391b6618dd
#   And of `4ft35t`@github for the OpenWrt mod in grep command.
#   https://gist.github.com/4ft35t/510897486bc6986d19cac45b3b9ca1d0    

DOMAIN=''
CF_EMAIL=''
CF_ZONEID=''
CF_KEY=''
CF_NS='elle.ns.cloudflare.com'
INTERFACE='br-lan'
TMPREC=/tmp/cfddnsv6.addr

######
CF_DNSRECID=__RECID__
# Note: this line will be replaced on first run with auctual id from cloudflare.
#       See function updaterecid()
######

######
INET6IDNT='\/64 scope global dynamic'
# Note: the identical line of address varies in different distro.
# (Debian) FOR DHCPv6 Address:      '/128 scope global dynamic'
# (Debian) FOR EUI64 SLAAC Address: '/64 scope global dynamic mngtmpaddr'
# (OpenWrt) EUI64 SLAAC Address: '/64 scope global dynamic'
# Do the check with command `ip address show dev INTERFACE`
######


__dir="$(cd "$(dirname "$0")" && pwd)"
__file="${__dir}/$(basename "$0")"

waitv6addr () {
#
# Some device got IPv6 Address latter at boot, need to wait a while.
#
    local IPV6=
    while [[ -z $IPV6 ]]; do
        IPV6=$(ip -6 addr show dev ${INTERFACE} | sed -n -E "s/^ +inet6 //;/${INET6IDNT}/p" | head -n 1 | cut -d/ -f1)
        [[ -z $IPV6 ]] && sleep 3
    done
    echo $IPV6
}

updaterecid () {
#
# Retrive the subdomian record id, and replace the variable in this script.
#
    local RECID=$(curl -k -s -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records?name=${DOMAIN}" \
     -H "X-Auth-Email: ${CF_EMAIL}" \
     -H "X-Auth-Key: ${CF_KEY}" \
     -H "Content-Type: application/json" \
    | sed 's/,/\n/g' | awk -F'"' '/id/{print $6}' | head -1)

    if [[ ! -z $RECID ]]; then
        sed -i "s/^CF_DNSRECID=__RECID__/CF_DNSRECID='${RECID}'/" $__file
    fi
}


LOCALv6=$(waitv6addr)

#
# Simple check before running.
#
if [[ -z $DOMAIN || -z $CF_EMAIL || -z $CF_KEY || -z $CF_ZONEID ]]; then
    echo "The script get your IPv6 address as: ${LOCALv6}"
    echo "But some/none of the cloudflare account info is missing."
    echo "FILL OUT THE VARIABLES AT THE TOP OF THIS SCRIPT BEFORE RUNNING. "
    exit 1
fi

#
# First run.
#
if [[ ${CF_DNSRECID} == "__RECID__" ]]; then
    updaterecid
    $__file
    exit 0
fi

if [[ ! -f $TMPREC ]]; then
    echo $LOCALv6 > $TMPREC
    /usr/bin/logger -t cfddnsv6 "First run, log LOCAL: ${LOCALv6} to $TMPREC"
    exit 0
else
    LASTv6=$(cat $TMPREC)
fi

#
# Real work here.
#
# DNSv6=$(dig +short AAAA $DOMAIN @${CF_NS} | head -n 1)
if [[ "$LOCALv6" != "$LASTv6" ]]; then
    echo $LOCALv6 > $TMPREC
    /usr/bin/logger -t cfddnsv6 "LOCAL: ${LOCALv6}, LASTv6:$LASTv6"
    /usr/bin/curl -k -s -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records/${CF_DNSRECID}" \
     -H "X-Auth-Email: ${CF_EMAIL}" \
     -H "X-Auth-Key: ${CF_KEY}" \
     -H "Content-Type: application/json" \
     --data '{"type":"AAAA","name":"'${DOMAIN}'","content":"'${LOCALv6}'","ttl":600,"proxied":false}' | /usr/bin/logger -t cfddnsv6
fi
