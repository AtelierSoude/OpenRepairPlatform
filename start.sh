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
    cd ./deployment
    docker-compose kill ateliersoude-postgres
    docker-compose rm -f ateliersoude-postgres
    docker-compose up -d --build ateliersoude-postgres
    docker-compose kill ateliersoude-postgres
}

function rebuild_app() {
    cd ./deployment
    docker-compose kill django
    docker-compose rm -f django
    docker-compose up -d --build django
    docker-compose kill django
}

function start_gunicorn() {
    # docker run --name ateliersoude-django-$USERLOWER \
        #     --volume $DIR:/ateliersoude \
        #     --network ateliersoude-$USERLOWER \
    #     --restart unless-stopped \
    #     --publish ${PORT:-8000}:8000 \
    #     --env LOGLEVEL=${LOGLEVEL:-INFO} \
    #     --env POSTGRES_DB=ateliersoude-postgres-$USERLOWER \
    #     --env DEVELOPMENT=1 \
    #     --detach \
    #     ateliersoude-django-app-$USERLOWER
    cd ./deployment
    docker-compose up
}

function start_dev_server() {
    cd ./deployment
    docker-compose up --force-recreate
}

function create_env_file(){
    touch ./deployment/.env;
    echo "Nom de l'utilisateur postgresql?"
    read POSTGRES_USER
    echo "Mot de passe de l'utilisateur postgresql?"
    read POSTGRES_PASSWORD
    echo "Nom de la base de donnees?"
    read POSTGRES_DB
    echo "Development server? (Please answer 1 or 0)"
    read DEVELOPMENT
    echo "Debug mode? (Please answer 1 or 0)"
    read DJANGO_DEBUG
    echo "Adresse du serveur SMTP?"
    read SMTP_HOST
    echo "Adresse electronique de notifications?"
    read EMAIL_ADRESSE
    echo "Mot de passe de l'adresse?"
    read EMAIL_PASSWORD

    echo "POSTGRES_USER=$POSTGRES_USER" >> ./deployment/.env
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> ./deployment/.env
    echo "POSTGRES_DB=$POSTGRES_DB" >> ./deployment/.env
    echo "DEVELOPMENT=$DEVELOPMENT" >> ./deployment/.env
    echo "DJANGO_DEBUG=$DJANGO_DEBUG" >> ./deployment/.env
    echo "SMTP_HOST=$SMTP_HOST" >> ./deployment/.env
    echo "EMAIL_ADRESSE=$EMAIL_ADRESSE" >> ./deployment/.env
    echo "EMAIL_PASSWORD='$EMAIL_PASSWORD" >> ./deployment/.env
}


function get_ports() {
    echo "************** external ports used by the docker container **************"
    echo `tput setaf 2`"Gunicorn main server: http://localhost:`docker port ateliersoude-django-$USERLOWER | head -1 | cut -d: -f2`/"`tput sgr0`
    echo "*************************************************************************"
}

case "${ACTION}" in
    "create_env")
        create_env_file
        ;;
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
    - create_env: create environment file for docker-compose, then fill in the environment variables
    - rebuild_db (postgres)
    - rebuild (gunicorn + static files)
    - reload (gunicorn, update for code changes, faster)
    - dev (launch dev server and keep a terminal open, static changes instantly visible)
Note that at first launch a rebuild_db is needed
EOF
        exit 1
        ;;
esac
