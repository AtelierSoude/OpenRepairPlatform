#!/bin/bash
# takes two paramters, the domain name and the email to be associated with the certificate
#DOMAINDNS=$1
#EMAIL=$2

# TODO : generate .env variables
#echo MARIADB_USER=matomo > .env.prod
#echo MARIADB_PASSWORD=`openssl rand 30 | base64 -w 0` >> .env.prod
#echo MARIADB_ROOT_PASSWORD=`openssl rand 30 | base64 -w 0` >> .env.prod
 
# Phase 1
docker compose -f ./docker-compose-initiate.prod.yml up -d nginx
docker compose -f ./docker-compose-initiate.prod.yml up certbot
docker compose -f ./docker-compose-initiate.prod.yml down
 
# some configurations for let's encrypt
curl -L --create-dirs -o ./deployment/nginx/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf
openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048
 
# Phase 2
#crontab /etc/crontab
docker compose -f ./docker-compose.prod.yml up -d