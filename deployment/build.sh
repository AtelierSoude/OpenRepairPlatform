#!/usr/bin/env bash

. openrepairplatform/.env
if [[ "${EMAIL_PASSWORD}" == "CHANGE_ME" || "${SECRET_KEY}" == "CHANGE_ME" ]]; then
    cat deployment/checklist.txt;
    exit 1;
fi

sudo docker pull postgres:11
sudo docker build -t openrepairplatform_nginx -f deployment/nginx/Dockerfile .
sudo docker build -t openrepairplatform_python -f deployment/django/Dockerfile .
