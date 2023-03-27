################ BASE #########################
FROM python:3.9.6-slim-buster AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN apt-get install -y libproj-dev locales locales-all cron gdal-bin build-essential sass

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
RUN useradd -ms /bin/bash -r -g openrepairplatform openrepairplatform
RUN usermod -G openrepairplatform,www-data openrepairplatform
RUN chown -R openrepairplatform:openrepairplatform /srv/*

#RUN mkdir /var/uwsgi
#RUN touch /var/uwsgi/openrepairplatform.sock
#RUN chown openrepairplatform:www-data /var/uwsgi
#RUN chown openrepairplatform:www-data /var/uwsgi/openrepairplatform.sock
#RUN chmod 660 /var/uwsgi/openrepairplatform.sock



# set work directory
WORKDIR /srv/app


# install dependencies
COPY ../../requirements.txt ./
COPY ../../requirements_dev.txt /srv/app/requirements_dev.txt 

RUN pip install -r requirements_dev.txt
RUN pip install uwsgi 

#RUN apt-get install -y yarn python3-pip make sassc binutils 


#RUN ln /usr/bin/sassc /usr/bin/sass
COPY manage.py . 

COPY deployment/django/start.sh .


################ BUILDER #########################
FROM base AS builder

WORKDIR /srv/app




COPY ../../openrepairplatform ./openrepairplatform



RUN cd ./openrepairplatform/static && npm install && node build.prod.js

RUN python3 manage.py collectstatic --noinput

################ DEVEVOPPEMENT #########################

FROM base AS developpement

WORKDIR /srv/app


RUN chmod 0644 /etc/cron.d/openrepairplatform
RUN cron

################ PRODUCTION #########################

FROM base AS production

WORKDIR /srv/app

ARG DOMAINDNS
ARG DOMAINS


COPY ../../openrepairplatform ./openrepairplatform


COPY deployment/django/uwsgi.ini .

#RUN mkdir /srv/app/uwsig
#RUN chown -R www-data:www-data /srv/app/uwsig/
USER openrepairplatform
COPY --from=builder /srv/app/openrepairplatform/static/ /srv/static

USER root
RUN chown -R openrepairplatform:openrepairplatform /srv/*
EXPOSE 8000

CMD ./start.sh

