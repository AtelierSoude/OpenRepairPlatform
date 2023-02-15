################ BASE #########################
FROM python:3.9.6-slim-buster AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN apt-get install -y libproj-dev locales locales-all cron gdal-bin

RUN pip install --upgrade pip

# French ENV for date
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL fr_FR
ENV LANG fr_FR
ENV LANGUAGE fr_FR

RUN mkdir -p /srv/app /srv/static /srv/media

COPY deployment/django/openrepairplatform.cron /etc/cron.d/openrepairplatform
RUN chmod 0644 /etc/cron.d/openrepairplatform

RUN groupadd -r openrepairplatform 
RUN  useradd -ms /bin/bash -r -g openrepairplatform openrepairplatform
RUN chown -R openrepairplatform:openrepairplatform /srv/*

# set work directory
WORKDIR /srv/app

# install dependencies
COPY ../../requirements.txt ./
COPY ../../requirements_dev.txt /srv/app/requirements_dev.txt 
RUN pip install -r requirements_dev.txt

#RUN apt-get install -y yarn python3-pip make sassc binutils 


#RUN ln /usr/bin/sassc /usr/bin/sass

COPY manage.py . 

COPY deployment/django/start.sh .


################ BUILDER #########################
FROM base AS builder

WORKDIR /srv/app

COPY ../../openrepairplatform ./openrepairplatform

RUN cd ./openrepairplatform/static && npm install && node build.prod.js

RUN chown -R openrepairplatform:openrepairplatform /srv/*
USER openrepairplatform
RUN python3 manage.py collectstatic --noinput

################ DEVEVOPPEMENT #########################

FROM base AS developpement

WORKDIR /srv/app

RUN chmod 0644 /etc/cron.d/openrepairplatform
RUN cron

################ PRODUCTION #########################

FROM base AS production

WORKDIR /srv/app

COPY ../../openrepairplatform ./openrepairplatform

USER root
RUN apt-get install -y uwsgi
COPY deployment/django/uwsgi.ini .

RUN sed -i "s/{{SECRET_KEY}}/${SECRET_KEY}/" /etc/cron.d/openrepairplatform
RUN sed -i "s/{{EMAIL_PASSWORD}}/${EMAIL_PASSWORD}/" /etc/cron.d/openrepairplatform

USER openrepairplatform

COPY --from=builder /srv/app/openrepairplatform/static/ /srv/static



CMD ./start.sh

