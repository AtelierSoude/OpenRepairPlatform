#!/usr/bin/env bash

if [[ $EUID -eq 0 ]]; then
  echo `tput setaf 1`"This script must NOT be run as root"`tput sgr0` 1>&2
  exit 1
fi

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
    docker network create \
        --driver bridge \
        ateliersoude-$USER
    docker build deployment/docker-db/ \
        --tag ateliersoude-postgres-$USER
    docker stop ateliersoude-postgres-$USER
    docker rm -f ateliersoude-postgres-$USER
    docker run --name ateliersoude-postgres-$USER \
        --env POSTGRES_PASSWORD=ateliersoude \
        --env POSTGRES_USER=ateliersoude \
        --network ateliersoude-$USER \
        --restart unless-stopped \
        --detach \
        ateliersoude-postgres-$USER
    echo "resting a bit..."
    sleep 10
}

function rebuild_app() {
    docker build deployment/docker-app/ \
        --tag ateliersoude-django-app-$USER
    docker stop ateliersoude-django-$USER
    docker rm -f ateliersoude-django-$USER
}

function start_gunicorn() {
    docker run --name ateliersoude-django-$USER \
        --volume $DIR:/ateliersoude \
        --network ateliersoude-$USER \
        --restart unless-stopped \
        --publish ${PORT:-8000}:8000 \
        --env LOGLEVEL=${LOGLEVEL:-INFO} \
        --env POSTGRES_DB=ateliersoude-postgres-$USER \
        --detach \
        ateliersoude-django-app-$USER
    }

function start_dev_server() {
    docker run --name ateliersoude-django-$USER \
        --env DJANGO_DEBUG=1 \
        --tty --interactive \
        --volume $DIR:/ateliersoude \
        --network ateliersoude-$USER \
        --publish ${PORT:-8001}:8001 \
        --env LOGLEVEL=${LOGLEVEL:-INFO} \
        --env POSTGRES_DB=ateliersoude-postgres-$USER \
        ateliersoude-django-app-$USER
}


function get_ports() {
    echo "************** external ports used by the docker container **************"
    echo `tput setaf 2`"Gunicorn main server: http://localhost:`docker port ateliersoude-django-$USER | head -1 | cut -d: -f2`/"`tput sgr0`
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
        docker exec -ti ateliersoude-django-$USER /bin/bash -c 'kill -HUP `pgrep -f gunicorn:\ master` 2>/dev/null'
        if [ "$?" -eq 0 ]; then echo OK; else echo FAIL; fi
        ;;
    *)
        cat <<EOF
$0 <action> [<port> [<loglevel>]]: Specify an action:
    - rebuild_db (postgres)
    - rebuild (gunicorn + static files)
    - reload (gunicorn, update for code changes, faster)
    - dev (launch dev server and keep a terminal open, static changes instantly visible)
Note that at first launch a rebuild_db is needed
EOF
        exit 1
        ;;
esac
