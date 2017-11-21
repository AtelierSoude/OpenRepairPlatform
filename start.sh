#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ACTION="$1"
PORT="$2"
LOGLEVEL="$3"

# todo make this be loaded on container startup from docker secrets
# this is used by the build script to set the super user login and pass for the postgres db
# also change it in the settings.py file
export POSTGRES_USER=ateliersoude
export POSTGRES_PASSWORD=ateliersoude

function rebuild_db() {
    docker network create --driver bridge ateliersoude
    docker build deployment/docker-db/ --tag ateliersoude-postgres
    docker stop ateliersoude-postgres
    docker rm -f ateliersoude-postgres
    docker run --name ateliersoude-postgres --env POSTGRES_PASSWORD=ateliersoude \
        --env POSTGRES_USER=ateliersoude --network ateliersoude \
        --restart unless-stopped --detach ateliersoude-postgres
    echo "resting a bit..."
    sleep 10
}

function rebuild_app() {
    docker build deployment/docker-app/ --tag ateliersoude-django-app
    docker stop ateliersoude-django
    docker rm -f ateliersoude-django
}

function start_gunicorn() {
    docker run --name ateliersoude-django \
        --volume $DIR:/ateliersoude \
        --network ateliersoude \
        --restart unless-stopped \
        --publish ${PORT:-8000}:8000 \
        --env LOGLEVEL=${LOGLEVEL:-INFO} \
        --detach \
        ateliersoude-django-app
    }

function start_dev_server() {
    docker run --name ateliersoude-django \
        --env DJANGO_DEBUG=1 \
        --tty --interactive \
        --volume $DIR:/ateliersoude \
        --network ateliersoude \
        --publish ${PORT:-8001}:8001 \
        ateliersoude-django-app
}


function get_ports() {
    echo "************** external ports used by the docker container **************"
    docker port ateliersoude-django
    echo `tput setaf 2`"Gunicorn main server: http://localhost:`docker port ateliersoude-django | grep 8000 | cut -d: -f2`"`tput sgr0`
    echo "*************************************************************************"
}

case "${ACTION}" in
    "rebuild_db")
        rebuild_db
        ;;
    "rebuild")
        rebuild_app
        start_gunicorn
        get_ports
        ;;
    "dev")
        DEBUG=" --env DJANGO_DEBUG=1 "
        rebuild_app
        echo `tput setaf 2`"Dev server starting, no need to CTRL-C + reload to see changes, keep it running"`tput sgr0`
        start_dev_server
        ;;
    "reload")
        docker exec -ti ateliersoude-django /bin/bash -c 'kill -HUP `pgrep -f gunicorn:\ master` 2>/dev/null'
        if [ "$?" -eq 0 ]; then echo OK; else echo FAIL; fi
        ;;
    *)
        cat <<EOF
$0 : Specify a command:
    - rebuild_all (gunicorn + static files + postgres)
    - rebuild (gunicorn + static files)
    - reload (gunicorn)
    - debug (launch dev server and keep a tty, no need to collectstatic)
EOF
        exit 1
        ;;
esac
