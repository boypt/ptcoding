#!/usr/bin/env bash
#!/usr/bin/env sh # for openwrt

#
# Cloudflare API Dynamic AAAA DNS Updater for IPv6 addresse in Bash
#
# Credit:
#   Part of this script got inspired from the work of `benkulbertis`@github:
#   https://gist.github.com/benkulbertis/fff10759c2391b6618dd
#   And of `4ft35t`@github for the OpenWrt mod in grep command.
#   https://gist.github.com/4ft35t/510897486bc6986d19cac45b3b9ca1d0    

DOMAIN=''
CF_AUTH=''
CF_ZONEID=''
CF_NS='elle.ns.cloudflare.com'
TMPREC=/tmp/cfddnsv6.addr

######
CF_DNSRECID=__RECID__
# Note: this line will be replaced on first run with auctual id from cloudflare.
#       See function updaterecid()
######

if ! command -v ip >/dev/null 2>&1; then
  echo "iproute2 tool not found."
  exit 1
fi

__dir="$(cd "$(dirname "$0")" && pwd)"
__file="${__dir}/$(basename "$0")"

METHOD=$1
LAST_FROMDNS=0
LAST_FROMLOCAL=0
case $METHOD in
    dns)
    LAST_FROMDNS=1
    ;;
    local)
    LAST_FROMLOCAL=1
    ;;
    *)
    LAST_FROMDNS=1
    ;;
esac

findv6addr () {
    local IPV6=
    local FOUNDSRC=0
    for ADDR in $(ip route get 2606:4700:4700::1111 | head -n1); do
        if [[ "x${ADDR}" == "xsrc" ]]; then
          FOUNDSRC=1
          continue
        fi
        if [[ $FOUNDSRC -eq 1 ]]; then
          IPV6=$ADDR
          FOUNDSRC=0
          break
        fi
    done
    echo $IPV6
}

updaterecid () {
#
# Retrive the subdomian record id, and replace the variable in this script.
#
    local RECID=$(curl -k -s -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records?name=${DOMAIN}" \
     -H "Authorization: Bearer ${CF_AUTH}" \
     -H "Content-Type: application/json" \
    | sed 's/,/\n/g' | awk -F'"' '/id/{print $6}' | head -1)

    if [[ ! -z $RECID ]]; then
        sed -i "s/^CF_DNSRECID=__RECID__/CF_DNSRECID='${RECID}'/" $__file
    fi
}

#
# Simple check before running.
#
if [[ -z $DOMAIN || -z $CF_AUTH || -z $CF_ZONEID ]]; then
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

# 
# Read last REC from tempdir (or from NS)
#
LOCALv6=$(findv6addr)
if [[ $LAST_FROMLOCAL -eq 1 ]]; then
    if [[ ! -f $TMPREC ]]; then
        echo $LOCALv6 > $TMPREC
        LASTv6=$(dig +short AAAA $DOMAIN @${CF_NS} | head -n 1)
        /usr/bin/logger -t cfddnsv6 "First run, query NS for LASTADDR: ${LASTv6}, LOCALv6: ${LOCALv6}"
    else
        LASTv6=$(cat $TMPREC)
    fi
fi

if [[ $LAST_FROMDNS -eq 1 ]]; then
    LASTv6=$(dig +short AAAA $DOMAIN @${CF_NS} | head -n 1)
fi

#
# Real work here.
#
if [[ "$LOCALv6" != "$LASTv6" ]]; then
    /usr/bin/logger -t cfddnsv6 "LOCAL: ${LOCALv6}, LASTv6:${LASTv6}"
    /usr/bin/curl -k -s -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records/${CF_DNSRECID}" \
     -H "Authorization: Bearer ${CF_AUTH}" \
     -H "Content-Type: application/json" \
     --data '{"type":"AAAA","name":"'${DOMAIN}'","content":"'${LOCALv6}'","ttl":600,"proxied":false}' | /usr/bin/logger -t cfddnsv6 && \
     echo $LOCALv6 > $TMPREC
fi
