#!/bin/sh

XWARE_DIR=/root/xware
XWARE=$XWARE_DIR/etm_xware
MOUNTS=$XWARE_DIR/thunder_mounts.cfg
ETMINI=$XWARE_DIR/etm.ini
LOGINI=$XWARE_DIR/log.ini
HUBBLE_PIPE=/tmp/hub.pipe
PID=/tmp/etm.pid
LICENSE=1508062001000004u0000007vub32aatrnhgtpuwdz
LISTEN=0.0.0.0:19000
ETM_URL=http://127.0.0.1:19000/getsysinfo

####
MONPID=/tmp/etm_mon.pid
####


util_kill () {
    local pid=$1
    echo "Killing PID $pid"
    kill $pid
}

xware_start () {
( ${XWARE} --system_path="$XWARE_DIR" --disk_cfg="$MOUNTS" --etm_cfg="$ETMINI" --log_cfg="$LOGINI" --pid_file="$PID" --license="$LICENSE" --import_v1v2_mode=2 --listen_addr="$LISTEN" --hubble_report_pipe_path="$HUBBLE_PIPE" | logger & )
}

xware_status () {
    if kill -0 `cat $PID` > /dev/null 2>&1; then
        echo "xware running"
    else
        echo "xware dead"
    fi
}

xware_check () {
    if ! wget -q -s http://127.0.0.1:19000/getsysinfo > /dev/null 2>&1; then
        xware_start
    fi
}

xware_monitor () {
    while true; do
        xware_check
        sleep 30
    done
}

case "$1" in
        start)
            xware_start
            ;;
        stop)
            util_kill `cat $PID`
            ;;
        monstop)
            util_kill `cat $MONPID`
            ;;
        status)
            xware_status
            ;;
        restart)
            xware_stop
            xware_start
            ;;
        check)
            xware_check
            ;;
        monitor)
            xware_monitor &
            echo $! > $MONPID
            ;;
        *)
            echo $"Usage: $0 {start|stop|restart|status|monitor|monstop}"
            exit 1
esac

