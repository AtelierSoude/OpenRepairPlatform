#!/usr/bin/env bash

. deployment/django/django.env
if [[ "${EMAIL_PASSWORD}" == "CHANGE_ME" || "${SECRET_KEY}" == "CHANGE_ME" ]]; then
    cat deployment/checklist.txt;
    exit 1;
fi

sudo docker network create ateliersoude || true

sudo docker run \
    --name=postgres \
    --env-file=deployment/postgres/postgres.env \
    -d --restart=unless-stopped \
    -v $PWD/postgres_data:/var/lib/postgresql/data \
    --network=ateliersoude \
    postgres:11
sudo docker run \
    --name=ateliersoude_python \
    -d --restart=unless-stopped \
    --env-file=deployment/django/django.env \
    -v $PWD/ateliersoude_static:/srv/static \
    -v $PWD/ateliersoude_media:/srv/media \
    --network=ateliersoude \
    ateliersoude_python
sudo docker run \
    --name=ateliersoude_nginx \
    -p 8000:80 \
    -d --restart=unless-stopped \
    -v $PWD/ateliersoude_static:/srv/static:ro \
    -v $PWD/ateliersoude_media:/srv/media:ro \
    --network=ateliersoude \
    ateliersoude_nginx
