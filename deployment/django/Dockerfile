
################ BASE #########################
FROM python:3.9-slim-buster AS base

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl 
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN apt-get install -y yarn python3-pip locales locales-all cron make sassc binutils libproj-dev gdal-bin

RUN groupadd -r openrepairplatform 
RUN  useradd -r -g openrepairplatform openrepairplatform

# French ENV for date
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL fr_FR
ENV LANG fr_FR
ENV LANGUAGE fr_FR

RUN mkdir /srv/app /srv/static /srv/media
WORKDIR /srv/app

COPY ../../requirements.txt ./
RUN pip3 install -r ./requirements.txt

RUN ln /usr/bin/sassc /usr/bin/sass

COPY manage.py . 
COPY deployment/django/openrepairplatform.cron /etc/cron.d/openrepairplatform
RUN chmod 0644 /etc/cron.d/openrepairplatform

COPY deployment/django/start.sh .



################ BUILDER #########################
FROM base AS builder

WORKDIR /srv/app

COPY ../../openrepairplatform ./openrepairplatform

RUN cd ./openrepairplatform/static  && npm install && node build.prod.js

RUN chown -R openrepairplatform:openrepairplatform /srv/*
USER openrepairplatform
RUN python3 ./manage.py collectstatic --noinput

################ DEVEVOPPEMENT #########################

FROM base AS developpement

WORKDIR /srv/app

COPY ../../requirements_dev.txt /srv/app/requirements_dev.txt 
RUN pip3 install -r /srv/app/requirements_dev.txt 
RUN rm /srv/app/requirements_dev.txt

RUN chmod 0644 /etc/cron.d/openrepairplatform
RUN cron

################ PRODUCTION #########################

FROM base AS production

RUN pip3 install uwsgi
COPY deployment/django/uwsgi.ini .

COPY --from=builder /srv/app/openrepairplatform/static/ /srv/static

RUN sed -i "s/{{SECRET_KEY}}/${SECRET_KEY}/" /etc/cron.d/openrepairplatform
RUN sed -i "s/{{EMAIL_PASSWORD}}/${EMAIL_PASSWORD}/" /etc/cron.d/openrepairplatform

CMD /start.sh

