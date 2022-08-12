#!/bin/sh
AUTHKEY="$HOME/.ssh/authorized_keys"
[ -d $HOME/.ssh ] || mkdir -p -m 700 $HOME/.ssh
[ -f $AUTHKEY ] || touch $AUTHKEY
[ $(stat -c '%a' $AUTHKEY) -eq 600 ] || chmod 600 $AUTHKEY;
[ -z "$(tail -c 1 $AUTHKEY)" ] || echo "" >> $AUTHKEY
command -v selinuxenabled && selinuxenabled && restorecon -R -v $HOME/.ssh
cat >> $AUTHKEY << EOF
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIELiYCg8t270YczeBAOBuWAiOCKgMUNRjJGUNrZk8ce pt@hlap
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIBsKxhfGF6VRITv8htdPvVgjaFH9mwYj97q4SEn7Po/ pt25@desk
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJq24Y18v06FTfCUUYIzTDwZxZQKAfc+EciL/s6AZYKW pt25@mob
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOdHg8Gc+q0x8LwcpBYta0tal2v2nJhU8/tobhZ+60LZ pt25@lap
EOF
echo "Done Adding Keys. --"
