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

CF_AUTH=''
CF_ZONEID=''
CF_NS='elle.ns.cloudflare.com'
TMPREC=/tmp/cfddnsv6.addr

######
CF_DOMAIN=''
CF_DNSRECID=''
# Note: Replace this line with `$0 785a4c0d12c84640eabd5991fcb00a64`
#       See function updaterecid()
######

if ! command -v ip >/dev/null 2>&1; then
  echo "iproute2 tool not found."
  exit 1
fi

__dir="$(cd "$(dirname "$0")" && pwd)"
__file="${__dir}/$(basename "$0")"

getrecid () {
#
# Retrive the subdomian record id, and replace the variable in this script.
#
    local cf_name=${1:-}
    [[ ! -z $cf_name ]] || return 1
    local RECID=$(curl -k -s -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records?name=${cf_name}" \
     -H "Authorization: Bearer ${CF_AUTH}" \
     -H "Content-Type: application/json" \
    | sed 's/,/\n/g' | awk -F'"' '/id/{print $6}' | head -1)

    echo $RECID
}

findsrcaddr () {
    local IPSRC=
    local FOUND=0
    for ADDR in $(ip route get $1 | head -n1); do
        [[ $FOUND -eq 1 ]] && IPSRC=$ADDR && break
        [[ "x${ADDR}" == "xsrc" ]] && FOUND=1 && continue
    done
    [[ -n IPSRC ]] && echo $IPSRC
}

update_record () {
    local up_recid=${1:-}
    local up_name=${2:-}
    local up_type=${3:-AAAA}
    local up_content=${4:-}

    /usr/bin/curl -k -s -X PUT \
    "https://api.cloudflare.com/client/v4/zones/${CF_ZONEID}/dns_records/${up_recid}" \
     -H "Authorization: Bearer ${CF_AUTH}" \
     -H "Content-Type: application/json" \
     --data '{"type":"'${up_type}'","name":"'${up_name}'","content":"'${up_content}'","ttl":600,"proxied":false}'
}

# MAIN
METHOD="${1:-}"
LAST_FROMDNS=0
LAST_FROMLOCAL=0
case $METHOD in
    getrecid)
    if [[ ! -z ${2:-} ]]; then
        getrecid ${2:-}
    else
        getrecid $CF_DOMAIN
    fi
    exit 0
    ;;
    dns)
    LAST_FROMDNS=1
    ;;
    local)
    LAST_FROMLOCAL=1
    ;;
    *)
    exit 1
    ;;
esac

#
# Simple check before running.
#
if [[ "" = "$CF_DOMAIN" || "" = "$CF_AUTH" || "" = "$CF_ZONEID" ]]; then
    echo "The script get your IPv6 address as: ${LOCALv6}"
    echo "But some/none of the cloudflare account info is missing."
    echo "FILL OUT THE VARIABLES AT THE TOP OF THIS SCRIPT BEFORE RUNNING. "
    exit 1
fi

#
# First run.
#
if [[ "${CF_DNSRECID}" = "" ]]; then
    getrecid "$CF_DOMAIN"
    echo "edit the script replace CF_DNSRECID with the value abouve"
    exit 1
fi

# 
# Read last REC from tempdir (or from NS)
#
LOCALv6=$(findsrcaddr 240c::)
if [[ $LAST_FROMLOCAL -eq 1 ]]; then
    if [[ ! -f $TMPREC ]]; then
        echo $LOCALv6 > $TMPREC
        LASTv6=$(dig +short AAAA $CF_DOMAIN @${CF_NS} | head -n 1)
        /usr/bin/logger -t cfddnsv6 "First run, query NS for LASTADDR: ${LASTv6}, LOCALv6: ${LOCALv6}"
    else
        LASTv6=$(cat $TMPREC)
    fi
fi

if [[ $LAST_FROMDNS -eq 1 ]]; then
    LASTv6=$(dig +short AAAA $CF_DOMAIN @${CF_NS} | head -n 1)
fi

#
# Real work here.
#
if [[ "$LOCALv6" != "$LASTv6" ]]; then
    /usr/bin/logger -t cfddnsv6 "LOCAL: ${LOCALv6}, LASTv6:${LASTv6}"
    update_record ${CF_DNSRECID} ${CF_DOMAIN} AAAA ${LOCALv6}
     echo $LOCALv6 > $TMPREC
fi
