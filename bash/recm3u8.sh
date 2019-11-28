#!/usr/bin/env bash
# Bash3 Boilerplate. Copyright (c) 2014, kvz.io

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace

# Set magic variables for current file & dir
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__file="${__dir}/$(basename "${BASH_SOURCE[0]}")"
__base="$(basename ${__file} .sh)"
__root="$(cd "$(dirname "${__dir}")" && pwd)" # <-- change this as it depends on your app

SKEY="${1:-}"

if [[ -z $SKEY ]]; then
  echo "need key"
  exit 1
fi


declare -A SRCS
SRCS["gs"]="http://satellitepull.cnr.cn/live/wxgdgsgb/playlist.m3u8"
SRCS["zj"]="http://satellitepull.cnr.cn/live/wxgdzjjjt/playlist.m3u8"
SRCS["gs2"]="http://ls.qingting.fm/live/4847/64k.m3u8?deviceid=00000000-2a50-2e6a-7cbf-0d991c12983e"
SRCS["zj2"]="http://ls.qingting.fm/live/1259/64k.m3u8?deviceid=00000000-2a50-2e6a-7cbf-0d991c12983e"
SRCS["gs3"]="http://ctt5.rgd.com.cn/fm953"
SRCS["zj3"]="http://ctt5.rgd.com.cn/fm974"

SRCINPUT=${SRCS[$SKEY]}
if [[ -z $SRCINPUT ]]; then  exit 1; fi

RECPATH=/srv/md/radio/audio

if [[ ! -d $RECPATH ]]; then
  RECPATH=/tmp
fi

RECNAME=${RECPATH}/[${SKEY}]-$(date '+%m-%d_%H:%M:%S')
#FFMPEGCMD="/usr/local/bin/ffmpeg -hide_banner -loglevel panic -re -i ${SRCINPUT} -c copy -bsf:a aac_adtstoasc ${RECNAME}.opus"
/usr/local/bin/ffmpeg -hide_banner -loglevel error -y -nostdin -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 2 -timeout 1000000 -re -i ${SRCINPUT} -fflags +genpts+igndts -multiple_requests 1 -c:a libopus -ab 12k -af "pan=mono|c0=.5*c0+.5*c1" ${RECNAME}.opus &
FFPID=$!
sleep 10
if kill -0 $FFPID; then
  /usr/local/bin/fdwatchdog -s opus -p $FFPID
fi

