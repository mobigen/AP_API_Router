app_name=API-Service
router_host=$1
router_port=$2
category=$3

input() {
    if [[ $router_host == "" ]];then
        router_host=192.168.100.126
    fi
    if [[ $router_port == "" ]];then
        router_port=9014
    fi
    if [[ $category == "" ]];then
        category=meta
    fi
}

router_start() {
    source_path="$( cd "$( dirname "$0" )" && pwd -P )"
    router_exec="nohup python3.8 ${source_path}/server.py --host ${router_host} --port ${router_port} --category ${category} 1> /dev/null 2>&1 &"
    echo "Start Command : ${router_exec}"
    nohup python3.8 ${source_path}/server.py --host ${router_host} --port ${router_port} --category ${category} 1> /dev/null 2>&1 &
}

echo "########## Start Application (${app_name}) ##########"
echo "========== START ${app_name} =========="
input

source_path="$( cd "$( dirname "$0" )" && pwd -P )"
make_dir="${source_path}/log"
mkdir $make_dir

router_start
