#!/bin/bash

auto_login_ssh () {
    expect -c "set timeout -1;
                spawn ssh -o StrictHostKeyChecking=no $2 ${@:3};
                expect *assword:*;
                send -- $1\r;
                interact;";
}

conn_to_ssh () {
    HOSTS=($(curl freessh.us | sed -n "s/.*<td bgcolor='#FFFFFF'>\([0-9a-z\.]\+\?\)<\/td>.*$/\1/p"))
    RND=$(($RANDOM % 2 * 3))
    HOST=${HOSTS[0+$RND]}
    USR=${HOSTS[1+$RND]}
    PSW=${HOSTS[2+$RND]}
    auto_login_ssh $PSW $USR@$HOST -D 7070 -N
}

while true; do
    conn_to_ssh
done

