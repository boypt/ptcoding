#!/bin/bash

if ! id www-data; then
  groupadd --system www-data
  useradd -g www-data --no-user-group --home-dir /var/www --shell /usr/sbin/nologin --system www-data
fi
mkdir -p /etc/ssl/caddy /etc/caddy/
chown root:www-data /etc/ssl/caddy 
chmod 0770 /etc/ssl/caddy

curl https://getcaddy.com | bash -s personal
curl -Lv -o /etc/systemd/system/caddy.service https://raw.githubusercontent.com/caddyserver/caddy/master/dist/init/linux-systemd/caddy.service
base64 -d > "/etc/systemd/system/v2""ra""y.service" <<EOF
W1VuaXRdCkRlc2NyaXB0aW9uPVYyUmF5IFNlcnZpY2UKQWZ0ZXI9bmV0d29yay50YXJnZXQKV2Fu
dHM9bmV0d29yay50YXJnZXQKCltTZXJ2aWNlXQpUeXBlPXNpbXBsZQpVc2VyPXd3dy1kYXRhCkdy
b3VwPXd3dy1kYXRhClBJREZpbGU9L3J1bi92MnJheS5waWQKRXhlY1N0YXJ0PS91c3IvYmluL3Yy
cmF5L3YycmF5IC1jb25maWcgL2V0Yy92MnJheS9jb25maWcuanNvbgpSZXN0YXJ0PW9uLWZhaWx1
cmUKUmVzdGFydFByZXZlbnRFeGl0U3RhdHVzPTIzCgpbSW5zdGFsbF0KV2FudGVkQnk9bXVsdGkt
dXNlci50YXJnZXQK
EOF
systemctl daemon-reload
