app_name=API-Router
router_host=$1
router_port=$2
router_db=$3

input() {
    if [[ $router_host == "" ]];then
        router_host=0.0.0.0
    fi
    if [[ $router_port == "" ]];then
        router_port=8010
    fi
    if [[ $router_db == "" ]];then
        router_db=test
    fi
}

router_stop() {
    app=$( ps -ef | grep python | grep uvicorn | grep ${router_host} | grep ${router_port} | awk '{print $2}' )
    if [[ $app != "" ]];then
        exit_app="kill -9 ${app}"
        echo "Stop Command ( router ) : "${exit_app}
        $exit_app
    else
        echo "Not Found application. ( router )"
    fi
}

router_start() {
    echo "APP_ENV :: $APP_ENV"
    source_path="$( cd "$( dirname "$0" )" && pwd -P )"
    export PYTHONPATH=$PYTHONPATH:$source_path
    router_exec="nohup uvicorn app.main:app --host ${router_host} --port ${router_port} --log-config app/logging.json &>/dev/null &"
    echo "Start Command : ${router_exec}"
    eval ${router_exec}
}

echo "########## Safe Start (${app_name}) ##########"
echo "========== STOP ${app_name} =========="
input

router_stop
sleep 2

echo "========== START ${app_name} =========="
router_start