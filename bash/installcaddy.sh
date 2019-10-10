#!/bin/bash

#caddy binary
curl https://getcaddy.com | bash -s personal

if ! id www-data; then
  groupadd --system www-data
  useradd -g www-data --no-user-group --home-dir /var/www --shell /usr/sbin/nologin --system www-data
fi
mkdir -p /etc/ssl/caddy
chown root:www-data /etc/ssl/caddy
chmod 0770 /etc/ssl/caddy

mkdir -p /etc/caddy/
#caddy service
curl -o /etc/systemd/system/caddy.service https://raw.githubusercontent.com/caddyserver/caddy/master/dist/init/linux-systemd/caddy.service


systemctl daemon-reload
