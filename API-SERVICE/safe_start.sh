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

router_stop() {
    app=$( ps -ef | grep python | grep server.py | grep ${router_host} | grep ${router_port} | awk '{print $2}' )
    if [[ $app != "" ]];then
        exit_app="kill -9 ${app}"
        echo "Stop Command ( router ) : "${exit_app}
        $exit_app
    else
        echo "Not Found application. ( router )"
    fi
}

uvicorn_stop() {
    uvicorn=$( netstat -nlp | grep ${router_host}':'${router_port} | awk '{print $7}' | tr "/" "\n" )
    if [[ $uvicorn != "" ]];then
        for i in $uvicorn
        do
            if [[ ${i} == *python* ]];then
                continue
            fi
            exit_uvicorn="kill -9 ${i}"
            echo "Stop Command ( uvicorn ) : "${exit_uvicorn}
            $exit_uvicorn
        done
    else
        echo "Not Found application. ( uvicorn )"
    fi
}

router_start() {
    source_path="$( cd "$( dirname "$0" )" && pwd -P )"
    router_exec="nohup python3.8 ${source_path}/server.py --host ${router_host} --port ${router_port} --category ${category} 1> /dev/null 2>&1 &"
    echo "Start Command : ${router_exec}"
    nohup python3.8 ${source_path}/server.py --host ${router_host} --port ${router_port} --category ${category} 1> /dev/null 2>&1 &
}

echo "########## Safe Start (${app_name}) ##########"
echo "========== STOP ${app_name} =========="
input

router_stop
sleep 2
uvicorn_stop

echo "========== START ${app_name} =========="
router_start
