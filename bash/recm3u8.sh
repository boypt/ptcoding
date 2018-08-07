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


declare -A SRCS
SRCS["gs"]="http://satellitepull.cnr.cn/live/wxgdgsgb/playlist.m3u8"
SRCS["zj"]="http://satellitepull.cnr.cn/live/wxgdzjjjt/playlist.m3u8"
SRCS["gs2"]="http://ls.qingting.fm/live/4847/64k.m3u8?deviceid=00000000-2a50-2e6a-7cbf-0d991c12983e"
SRCS["zj2"]="http://ls.qingting.fm/live/1259/64k.m3u8?deviceid=00000000-2a50-2e6a-7cbf-0d991c12983e"

SRCINPUT=${SRCS[$SKEY]}
if [[ -z $SRCINPUT ]]; then  exit 1; fi

RECPATH=/srv/md/radio/audio

if [[ ! -d $RECPATH ]]; then
  RECPATH=.
fi

RECNAME=${RECPATH}/[${SKEY}]-$(date '+%m-%d_%H:%M:%S')
#FFMPEGCMD="/usr/local/bin/ffmpeg -hide_banner -loglevel panic -re -i ${SRCINPUT} -c copy -bsf:a aac_adtstoasc ${RECNAME}.opus"
FFMPEGCMD="/usr/local/bin/ffmpeg -hide_banner -loglevel panic -re -i ${SRCINPUT} -multiple_requests 1 -c:a libopus -ab 12k -af pan=mono|c0=.5*c0+.5*c1 ${RECNAME}.opus"

killall -q ffmpeg || true
${FFMPEGCMD} &

