
FROM debian:buster

RUN apt update -y && apt upgrade -y
RUN apt install -y nginx certbot

CMD sed -i "s/{{DOMAINE_NAME}}/${DOMAINE_NAME}/g" /deployment/nginx/nginx.conf
COPY deployment/nginx/nginx.conf /etc/nginx/sites-enabled/default
COPY deployment/nginx/nginx-snippet.conf /etc/nginx/snippets/ssl-params.conf

RUN mkdir /var/www/letsencrypt
RUN mkdir /var/www/letsencrypt/.well-known
RUN mkdir /var/www/letsencrypt/.well-known/acme-challenge

#command to run on first exec to generate diffie helman cert use to secure tls handshake
CMD openssl dhparam -out /etc/ssl/certsdhparam.pem 4096

CMD while :; do sleep 12h & wait ${!}; certbot renew; nginx -s reload; done & nginx -g "daemon off;"

