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

RECPATH=/srv/md/mp4
RECNAME=${RECPATH}/gz-$(date '+%m%d-%H%M%S')
#FFMPEGCMD="/usr/local/bin/ffmpeg -hide_banner -loglevel panic -re -i http://satellitepull.cnr.cn/live/wxgdgsgb/playlist.m3u8  -c copy -bsf:a aac_adtstoasc"
FFMPEGCMD="/usr/local/bin/ffmpeg -hide_banner -loglevel panic -re -i http://satellitepull.cnr.cn/live/wxgdgsgb/playlist.m3u8 -c:a libopus -ab 64k -af pan=mono|c0=.5*c0+.5*c1 ${RECNAME}.opus"

killall -q ffmpeg || true
${FFMPEGCMD} &

