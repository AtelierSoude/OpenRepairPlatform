#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# todo make this be loaded on container startup from docker secrets
export POSTGRES_USER=ateliersoude
export POSTGRES_PASSWORD=ateliersoude

function rebuild_db() {
    docker network create --driver bridge ateliersoude
    docker build deployment/docker-db/ --tag ateliersoude-postgres
    docker stop ateliersoude-postgres
    docker rm -f ateliersoude-postgres
    docker run --name ateliersoude-postgres --env POSTGRES_PASSWORD=ateliersoude --env POSTGRES_USER=ateliersoude --network ateliersoude --restart unless-stopped --detach ateliersoude-postgres
}

function rebuild_app() {
    echo "run this script with DEBUG=<something> to have django pick up the setting from the environment"
    if [[ ! -z "$DEBUG" ]]; then DEBUG=' --env DJANGO_DEBUG=1 '; fi
    docker build deployment/docker-app/ --tag ateliersoude-django-app
    docker stop ateliersoude-django
    docker rm -f ateliersoude-django
    docker run --name ateliersoude-django $DEBUG --volume $DIR:/ateliersoude --network ateliersoude --restart unless-stopped --publish 8000 --publish 8001 $DETACH ateliersoude-django-app
}

function get_ports() {
    echo "************** external ports used by the docker container **************"
    docker port ateliersoude-django
    echo "Gunicorn main server: http://localhost:`docker port ateliersoude-django | grep 8000 | cut -d: -f2`"
    echo "Dev server (not started by default): http://localhost:`docker port ateliersoude-django | grep 8001 | cut -d: -f2`"
    echo "*************************************************************************"
}

case $1 in
    "rebuild_all")
        DETACH="--detach"
        rebuild_db
        rebuild_app
        get_ports
        ;;
    "rebuild")
        DETACH="--detach"
        rebuild_app
        get_ports
        ;;
    "debug")
        DETACH="--tty --interactive"
        rebuild_app
        get_ports
        ;;
    "reload")
        docker exec -ti ateliersoude-django /bin/bash -c 'kill -HUP `pgrep -f gunicorn:\ master`'
        if [ "$?" -eq 0 ]; then echo OK; else echo FAIL; fi
        ;;
    *)
        echo "specify a command: rebuild, reload"
        exit 1
        ;;
esac
