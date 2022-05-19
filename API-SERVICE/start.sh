app_name=API-Service
router_host=$1
router_port=$2

input() {
    if [[ $router_host == "" ]];then
        router_host=192.168.101.44
    fi
    if [[ $router_port == "" ]];then
        router_port=19000
    fi
}

router_start() {
    source_path="$( cd "$( dirname "$0" )" && pwd -P )"
    router_exec="nohup python ${source_path}/server.py --host ${router_host} --port ${router_port} 1> /dev/null 2>&1 &"
    echo "Start Command : ${router_exec}"
    nohup python ${source_path}/server.py --host ${router_host} --port ${router_port} 1> /dev/null 2>&1 &
}

echo "########## Start Application (${app_name}) ##########"
echo "========== START ${app_name} =========="
input
router_start
