#!/usr/bin/env bash
# Bash3 Boilerplate. Copyright (c) 2014, kvz.io

set -o errexit
set -o pipefail
# set -o nounset
# set -o xtrace

# Set magic variables for current file & dir
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename ${__file} .sh)"
__root="$(cd "$(dirname "${__dir}")" && pwd)" # <-- change this as it depends on your app

arg1="${1:-}"

# allow command fail:
# fail_command || true

IDLE_TIME=60
HDPARM="/sbin/hdparm"
RAMDIR="/dev/shm"
HD_LIST="/dev/sda"
LAST_DS="null"

function CMD_SPINDOWN() {
    local cmd
    printf -v cmd "$HDPARM -y %s" "$1"
    exec $cmd > /dev/null 2>&1
}

function CMD_GET_APM_LEVEL() {
    local cmd
    printf -v cmd "$HDPARM -B %s" "$1"
    exec $cmd | awk -F '=' '/APM/{gsub(/ /, "", $2);print $2}'
}

function CMD_GET_STATUE() {
    local cmd
    printf -v cmd "$HDPARM -C %s" "$1"
    exec $cmd | awk -F ':' '/state/{gsub(/ /, "", $2);print $2}'
}

function TIMETS() {
    date +%s
}

function MAIN() {
    declare -A DSDATA
    local SLEEP_TIME=$((IDLE_TIME/10))
    if [[ $SLEEP_TIME -lt 10 ]]; then
        SLEEP_TIME=10
    fi

    for DISK in "$HD_LIST"; do
        local APMLEVEL=$(CMD_GET_APM_LEVEL $DISK)
        printf -v info "sd-idle: %s APM %s" $DISK $APMLEVEL
        logger $info
    done

    while true; do 
        local TS=$(TIMETS)
        for DISK in "$HD_LIST"; do
            local devname=$(basename $DISK)

            ##     8       0 sda 691 0 34826 432448 19 80 768 60 0 33900 432508
            ##    $6: READ, $10: WRITE
            printf -v awkptn  $devname
            local CURR_RW=$(awk "/ $devname /{print \$6,\$10}" /proc/diskstats)

            if [[ -z "${DSDATA[${devname}RW]}" ]]; then
                DSDATA[${devname}RW]=$CURR_RW
                DSDATA[${devname}TS]=$TS
                logger "$devname data empty. add: ${DSDATA[${devname}RW]}, ts: ${DSDATA[${devname}TS]} "
            else
                logger "$devname curr_rw $CURR_RW, last_rw: ${DSDATA[${devname}RW]}"
                if [[ "$CURR_RW" == "${DSDATA[${devname}RW]}" ]]; then
                    logger "$devname RW unchanged, TSDIFF: $((TS-${DSDATA[${devname}TS]}))"

                    if [[ $TS -ge $(( ${DSDATA[${devname}TS]} + $IDLE_TIME )) ]]; then
                        local STATUE=$(CMD_GET_STATUE $DISK)

                        logger "$devname statue: $STATUE "
                        if [[ $STATUE != "standby" ]]; then
                            logger "$devname going spindown"
                            CMD_SPINDOWN $DISK || true
                        else
                            logger "$devname is in standby"
                        fi

                    fi
                fi
            fi
        done

        sleep $SLEEP_TIME
    done
}

MAIN
