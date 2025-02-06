############### BASE #########################
FROM python:3.9.17-slim-buster AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update --fix-missing
RUN set -uex; \
    apt-get install -y ca-certificates curl gnupg; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
     | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; \
    NODE_MAJOR=18; \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
     > /etc/apt/sources.list.d/nodesource.list; \
    apt-get update; \
    apt-get install nodejs -y;
RUN apt-get install -y libproj-dev locales locales-all cron gdal-bin build-essential sassc

RUN ln /usr/bin/sassc /usr/bin/sass

RUN pip install --upgrade pip

# French ENV for date
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL fr_FR
ENV LANG fr_FR
ENV LANGUAGE fr_FR
RUN mkdir -p /srv/app /srv/static /srv/media

# add user 
RUN groupadd -r openrepairplatform
RUN useradd -ms /bin/bash -r -g openrepairplatform openrepairplatform
RUN usermod -G openrepairplatform,www-data openrepairplatform
RUN chown -R openrepairplatform:openrepairplatform /srv/*

#uwisgi
RUN mkdir /var/uwsgi
RUN touch /var/uwsgi/openrepairplatform.sock
RUN chown openrepairplatform:www-data /var/uwsgi
RUN chown openrepairplatform:www-data /var/uwsgi/openrepairplatform.sock
RUN chmod 660 /var/uwsgi/openrepairplatform.sock

# set work directory
WORKDIR /srv/app

# install dependencies
COPY ../../requirements.txt ./
COPY ../../requirements_dev.txt /srv/app/requirements_dev.txt

RUN pip install -r requirements_dev.txt
RUN pip install uwsgi

# for cron
COPY deployment/django/openrepairplatform.cron /etc/cron.d/openrepairplatform
RUN chmod 0644 /etc/cron.d/openrepairplatform
RUN chown openrepairplatform:openrepairplatform /etc/default/locale
RUN crontab /etc/cron.d/openrepairplatform
RUN chmod u+s /usr/sbin/cron

#RUN ln /usr/bin/sassc /usr/bin/sass
COPY manage.py .

################ BUILDER #########################
FROM base AS builder

WORKDIR /srv/app

################ DEVEVOPPEMENT #########################

FROM base AS developpement

WORKDIR /srv/app/

RUN pip install ptvsd

WORKDIR /srv/app/

CMD deployment/django/start-dev.sh

################ PRODUCTION #########################

FROM base AS production

WORKDIR /srv/app
ARG DOMAINDNS
ARG DOMAINS

COPY ../../openrepairplatform /srv/app/openrepairplatform

WORKDIR /srv/app/openrepairplatform/static
RUN  npm install --unsafe-perm=true
RUN  npm run buildprod

WORKDIR /srv/app/
RUN python3 manage.py assets build
RUN python3 ./manage.py collectstatic --noinput --clear

COPY deployment/django/start.sh .
COPY deployment/django/uwsgi.ini .

COPY ../../openrepairplatform/static /srv/static

RUN chown -R openrepairplatform:openrepairplatform /srv/*

USER openrepairplatform
EXPOSE 8000

ENTRYPOINT ./start.sh