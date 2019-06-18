#!/usr/bin/env bash

. deployment/django/django.env
if [[ "${EMAIL_PASSWORD}" == "CHANGE_ME" || "${SECRET_KEY}" == "CHANGE_ME" ]]; then
    cat deployment/checklist.txt;
    exit 1;
fi

sudo docker pull postgres:11
sudo docker build -t ateliersoude_nginx -f deployment/nginx/Dockerfile .
sudo docker build -t ateliersoude_python -f deployment/django/Dockerfile .
