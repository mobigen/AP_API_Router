#!/bin/bash

root_path="$( cd "$( dirname "$0" )" && pwd -P )"
pid_path="$root_path/gunicorn-router.pid"

echo $pid_path

env_path="./.env"
if [ -f "$env_path" ]; then
    while IFS= read -r line; do
        export $line
        echo "$line"
    done < "$env_path"
fi

LISTEN_ADDRESS="0.0.0.0:30001"

# gunicorn 실행 명령어
start_gunicorn() {
    gunicorn app.main:app --bind ${LISTEN_ADDRESS} -c gunicorn.conf.py -D --pid $pid_path
    sleep 2
    pid=$(cat $pid_path)
    echo "Gunicorn started. PID: $pid"
}

# gunicorn 중지 명령어
stop_gunicorn() {
    if [ -f $pid_path ]; then
        pid=$(cat $pid_path)
        kill "$pid"
        rm $pid_path
        echo "Gunicorn stopped. PID: $pid"
    else
        echo "Gunicorn is not running."
    fi
}

# gunicorn 재실행 명령어
restart_gunicorn() {
    stop_gunicorn
    start_gunicorn
}

# gunicorn 실행 상태 확인
status_gunicorn() {
    if [ -f $pid_path ]; then
        pid=$(cat $pid_path)
        echo "Gunicorn is running. PID: $pid"
    else
        echo "Gunicorn is not running."
    fi
}

# 스크립트 옵션 처리
case "$1" in
    start)
        start_gunicorn
        ;;
    stop)
        stop_gunicorn
        ;;
    restart)
        restart_gunicorn
        ;;
    status)
        status_gunicorn
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
