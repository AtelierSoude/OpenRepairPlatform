FROM debian:buster

RUN apt update && apt upgrade -y
RUN apt install -y nginx

COPY deployment/nginx/nginx.conf /etc/nginx/sites-enabled/default

CMD /usr/sbin/nginx -g "daemon off;"
