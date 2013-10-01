#!/bin/bash

LOCAL_PORT=7070

auto_login_ssh () {
    expect -c "set timeout -1;
                spawn ssh -o StrictHostKeyChecking=no $2 ${@:3};
                expect *assword:*;
                send -- $1\r;
                interact;";
}

conn_to_ssh () {
    echo "Retriving servers list from freessh.us ...."
    HOSTS=($(curl freessh.us | sed -n "s/.*<td bgcolor='#FFFFFF'>\(.\+\?\)<\/td>.*$/\1/p"))
    ITMS=${#HOSTS[@]}
    
    for I in seq 0 7 $(($ITMS - 1)); do
        if [[ ${HOSTS[$I + 6]} == "正常" ]]; then
            IDX=$I
            break
        elif [[ $I -eq $(($ITMS - 7)) ]]; then
            echo -e "\nError: All server are busy, or something's wrong: \n\n${HOSTS[@]}"
            exit 1
        fi
    done

    HOST=${HOSTS[1+$IDX]}
    USR=${HOSTS[2+$IDX]}
    PSW=${HOSTS[3+$IDX]}
    echo "Connecting to ${HOSTS[0+$IDX]} $HOST"
    auto_login_ssh $PSW $USR@$HOST -NC -D $LOCAL_PORT
}

while true; do
    conn_to_ssh
done

