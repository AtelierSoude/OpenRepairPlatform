#!/usr/bin/env bash

. deployment/django/django.env
if [[ "${EMAIL_PASSWORD}" == "CHANGE_ME" || "${SECRET_KEY}" == "CHANGE_ME" ]]; then
    cat deployment/checklist.txt;
    exit 1;
fi

sudo docker network create openrepairplatform || true

sudo docker run \
    --name=postgres \
    --env-file=openrepairplatform/.env \
    -d --restart=unless-stopped \
    -v $PWD/postgres_data:/var/lib/postgresql/data \
    --network=openrepairplatform \
    postgres:11
sudo docker run \
    --name=openrepairplatform_python \
    -d --restart=unless-stopped \
    --env-file=dopenrepairplatform/.env \
    -v $PWD/openrepairplatform_static:/srv/static \
    -v $PWD/openrepairplatform_media:/srv/media \
    --network=openrepairplatform \
    openrepairplatform_python
sudo docker run \
    --name=openrepairplatform_nginx \
    -p 80:80 \
    -p 443:443 \
    -d --restart=unless-stopped \
    -v $PWD/openrepairplatform_static:/srv/static:ro \
    -v $PWD/openrepairplatform_media:/srv/media:ro \
    -v $PWD/openrepairplatform_letsencrypt:/etc/letsencrypt/:rw \
    --network=openrepairplatform \
    openrepairplatform_nginx
