#!/usr/bin/env bash
# Bash3 Boilerplate. Copyright (c) 2014, kvz.io

set -o errexit
set -o pipefail
set -o nounset
# set -o xtrace


setconfig () {
    while true; do
        echo "Enter mapping port number: (must be greater than 50000)"
        read PORT
        if echo $PORT | grep -q -E "^5[0-9]{4}$"; then
            break;
        fi
    done

    cat > /etc/ngrok.yml << EOF
    server_addr: "ittun.com:44433"
    tunnels: 
    ssh:
    remote_port: $PORT
    proto:
    tcp: ":22"
EOF

    cat /etc/ngrok.yml 
    echo "---------------------"
}

ARCH=$(uname -m)
ITTUN_URL=http://www.ittun.com/upload/17.4/
TEMPDIR=$(mktemp -d)

if [ $ARCH == "x86_64" ]; then
    FILE=linux64.zip
elif [ $ARCH == "i686" ]; then
    FILE=linux32.zip
else
    echo "Arch unsupported;"
    exit 1
fi

setconfig

echo "Selected $FILE";
URL=${ITTUN_URL}${FILE}
cd $TEMPDIR
wget $URL
unzip $FILE
UNDIR=${FILE%.*}
install -v -m755 ./$UNDIR/ngrok /usr/local/bin/
cd -
rm -rfv $TEMPDIR

sed -i -e '$i \ngrok -log=stdout -config=/etc/ngrok.yml start ssh >/dev/null 2>&1 &\n' /etc/rc.local
echo "---------------------"
cat /etc/rc.local
echo "Done"

