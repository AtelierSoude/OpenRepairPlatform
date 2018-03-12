#!/usr/bin/env bash

if [[ $EUID -eq 0 ]]; then
  echo `tput setaf 1`"This script must NOT be run as root"`tput sgr0` 1>&2
  exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ACTION="$1"
PORT="$2"
LOGLEVEL="$3"
USERLOWER="$(tr [A-Z] [a-z] <<< "$USER")"

# todo make this be loaded on container startup from docker secrets
# this is used by the build script to set the super user login and pass for the postgres db
# also change it in the settings.py file
export POSTGRES_USER=ateliersoude
export POSTGRES_PASSWORD=ateliersoude

function rebuild_db() {
    docker network create \
        --driver bridge \
        ateliersoude-$USERLOWER
    docker build deployment/docker-db/ \
        --tag ateliersoude-postgres-$USERLOWER
    docker stop ateliersoude-postgres-$USERLOWER
    docker rm -f ateliersoude-postgres-$USERLOWER
    docker run --name ateliersoude-postgres-$USERLOWER \
        --env POSTGRES_PASSWORD=ateliersoude \
        --env POSTGRES_USER=ateliersoude \
        --network ateliersoude-$USERLOWER \
        --restart unless-stopped \
        --detach \
        ateliersoude-postgres-$USERLOWER
    echo "resting a bit..."
    sleep 10
}

function rebuild_app() {
    docker build deployment/docker-app/ \
        --tag ateliersoude-django-app-$USERLOWER
    docker stop ateliersoude-django-$USERLOWER
    docker rm -f ateliersoude-django-$USERLOWER
}

function start_gunicorn() {
    docker run --name ateliersoude-django-$USERLOWER \
        --volume $DIR:/ateliersoude \
        --network ateliersoude-$USERLOWER \
        --restart unless-stopped \
        --publish ${PORT:-8000}:8000 \
        --env LOGLEVEL=${LOGLEVEL:-INFO} \
        --env POSTGRES_DB=ateliersoude-postgres-$USERLOWER \
        --env DEVELOPMENT=1 \
        --detach \
        ateliersoude-django-app-$USERLOWER
    }

function start_dev_server() {
    docker run --name ateliersoude-django-$USERLOWER \
        --env DJANGO_DEBUG=1 \
        --tty --interactive \
        --volume $DIR:/ateliersoude \
        --network ateliersoude-$USERLOWER \
        --publish ${PORT:-8001}:8001 \
        --env LOGLEVEL=${LOGLEVEL:-INFO} \
        --env POSTGRES_DB=ateliersoude-postgres-$USERLOWER \
        --env DEVELOPMENT=1 \
        ateliersoude-django-app-$USERLOWER
}


function get_ports() {
    echo "************** external ports used by the docker container **************"
    echo `tput setaf 2`"Gunicorn main server: http://localhost:`docker port ateliersoude-django-$USERLOWER | head -1 | cut -d: -f2`/"`tput sgr0`
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
        docker exec -ti ateliersoude-django-$USERLOWER /bin/bash -c 'kill -HUP `pgrep -f gunicorn:\ master` 2>/dev/null'
        if [[ "$?" -eq 0 ]]; then echo OK; else echo FAIL; fi
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
