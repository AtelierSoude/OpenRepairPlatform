FROM debian:buster

RUN apt update -y && apt upgrade -y
RUN apt install -y nginx certbot cron

COPY deployment/nginx/nginx.conf /etc/nginx/sites-enabled/default
COPY deployment/nginx/nginx-snippet.conf /etc/nginx/snippets/ssl-params.conf
COPY deployment/nginx/certbot.sh /etc/cron.daily/certbot

RUN mkdir /var/www/letsencrypt
RUN mkdir /var/www/letsencrypt/.well-known
RUN mkdir /var/www/letsencrypt/.well-known/acme-challenge

#CMD openssl dhparam -out /etc/ssl/certsdhparam.pem 4096

#VOLUME /var/www/letsencrypt/.well-known/acme-challenge

CMD /usr/sbin/nginx -g "daemon off;"
