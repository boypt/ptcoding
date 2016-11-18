#!/bin/bash
DOMAIN="www.400gb.com news.163.com gdl.lixian.vip.xunlei.com s.doubanio.com"
DNS="114.114.114.114 101.226.4.6 114.215.126.16 180.76.76.76 1.2.4.8"

for S in $DNS; do
  echo "DNS $S"
  for D in $DOMAIN; do
    IP=$(dig +short $D @$S 2>/dev/null| tail -1)
    echo -n "$D#$S -> $IP"
    curl "http://freeapi.ipip.net/$IP"
    sleep 1
    echo
  done
done
