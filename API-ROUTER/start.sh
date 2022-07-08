app_name=API-Router
router_host=$1
router_port=$2
router_db=$3

input() {
    if [[ $router_host == "" ]];then
        router_host=192.168.100.126
    fi
    if [[ $router_port == "" ]];then
        router_port=9010
    fi
    if [[ $router_db == "" ]];then
        router_db=test
    fi
}

router_start() {
    source_path="$( cd "$( dirname "$0" )" && pwd -P )"
    router_exec="nohup python3.8 ${source_path}/server.py --host ${router_host} --port ${router_port} 1> /dev/null 2>&1 &"
    echo "Start Command : ${router_exec}"
    nohup python3.8 ${source_path}/server.py --host ${router_host} --port ${router_port} --db_type ${router_db} 1> /dev/null 2>&1 &
}

echo "########## Start Application (${app_name}) ##########"
echo "========== START ${app_name} =========="
input

router_start
