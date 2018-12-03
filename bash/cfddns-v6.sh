#!/bin/bash

DOMAIN=''
CF_EMAIL=''
CF_KEY=''
CF_ZONEID=''
CF_NS='elle.ns.cloudflare.com'
INTERFACE='br-lan'
INET6IDNT='scope global dynamic'
CF_DNSRECID=__RECID__

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"

waitv6addr () {
    local IPV6=
    while [[ -z $IPV6 ]]; do
        IPV6=$(ip -6 addr show dev ${INTERFACE} | sed -n -E "s/^ +inet6 //;/${INET6IDNT}/p" | head -n 1 | cut -d/ -f1)
        [[ -z $IPV6 ]] && sleep 3
    done
    echo $IPV6
}

updaterecid () {
    local RECID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records?name=${DOMAIN}" \
     -H "X-Auth-Email: ${CF_EMAIL}" \
     -H "X-Auth-Key: ${CF_KEY}" \
     -H "Content-Type: application/json" \
    | sed 's/,/\n/g' | awk -F'"' '/id/{print $6}' | head -1)
    sed -i "s/^CF_DNSRECID=__RECID__/CF_DNSRECID='${RECID}'/" $__file
}

if [[ -z $DOMAIN || -z $CF_EMAIL || -z $CF_KEY || -z $CF_ZONEID ]]; then
    echo "FILL OUT INFO BEFORE RUNNING THE SCRIPT. "
    exit 1
fi

if [[ ${CF_DNSRECID} == "__RECID__" ]]; then
    updaterecid
    $__file
    exit 0
fi

LOCALv6=$(waitv6addr)
DNSv6=$(dig +short AAAA $DOMAIN @${CF_NS} | head -n 1)
if [[ "$LOCALv6" != "$DNSv6" ]]; then
    /usr/bin/logger -t cfddnsv6 "LOCAL: ${LOCALv6}, REMOTE:$DNSv6"
    /usr/bin/curl -k -s -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records/${CF_DNSRECID}" \
     -H "X-Auth-Email: ${CF_EMAIL}" \
     -H "X-Auth-Key: ${CF_KEY}" \
     -H "Content-Type: application/json" \
     --data '{"type":"AAAA","name":"'${DOMAIN}'","content":"'${LOCALv6}'","ttl":600,"proxied":false}' | /usr/bin/logger -t cfddnsv6
fi
