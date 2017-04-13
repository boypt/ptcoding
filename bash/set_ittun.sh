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
ARCH=$(uname -m)

# allow command fail:
# fail_command || true

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

URL=${ITTUN_URL}${FILE}
cd $TEMPDIR
wget $URL
unzip $FILE
UNDIR=${FILE%.*}
install -v -m755 ./$UNDIR/ngrok /usr/local/bin/
rm -rf $TEMPDIR

echo "Enter mapping port: (must be greater than 51000)"
read PORT

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
sed -e -i '$i \ngrok -log=stdout -config=/etc/ngrok.yml start ssh >/dev/null 2>&1 &\n' rc.local
echo "---------------------"
cat /etc/rc.local
echo "Done"

