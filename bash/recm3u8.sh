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

arg1="${1:-}"

#SRCINPUT="http://satellitepull.cnr.cn/live/wxgdgsgb/playlist.m3u8"
SRCINPUT="http://ls.qingting.fm/live/4847/64k.m3u8?deviceid=00000000-2a50-2e6a-7cbf-0d991c12983e"
RECPATH=/srv/md/radio/audio
RECNAME=${RECPATH}/$(date '+%m-%d_%H:%M:%S')
#FFMPEGCMD="/usr/local/bin/ffmpeg -hide_banner -loglevel panic -re -i ${SRCINPUT} -c copy -bsf:a aac_adtstoasc ${RECNAME}.opus"
FFMPEGCMD="/usr/local/bin/ffmpeg -hide_banner -loglevel panic -re -i ${SRCINPUT} -c:a libopus -ab 12k -af pan=mono|c0=.5*c0+.5*c1 ${RECNAME}.opus"

killall -q ffmpeg || true
${FFMPEGCMD} &

