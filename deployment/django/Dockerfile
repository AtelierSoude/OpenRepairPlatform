FROM python:3.9-slim-buster

RUN apt update && apt install -y --force-yes curl 
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN apt update && apt upgrade -y && apt install -y --force-yes yarn python3-pip locales locales-all cron make sassc binutils libproj-dev gdal-bin
RUN pip3 install uwsgi
RUN ln /usr/bin/sassc /usr/bin/sass

COPY requirements_dev.txt /
COPY requirements.txt /
RUN pip3 install -r /requirements_dev.txt && rm /requirements_dev.txt

# French ENV for date
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL fr_FR
ENV LANG fr_FR
ENV LANGUAGE fr_FR

RUN mkdir /srv/app /srv/static /srv/media

WORKDIR /srv/app

#COPY manage.py .
#COPY static/img/ openrepairplatform/static/img/
#COPY deployment/django/uwsgi.ini .
#COPY deployment/django/start.sh /
#COPY openrepairplatform ./openrepairplatform
COPY deployment/django/openrepairplatform.cron /etc/cron.d/openrepairplatform

#RUN cd openrepairplatform/static/ && npm i && node build.prod.js && cd -

RUN chmod 0644 /etc/cron.d/openrepairplatform
RUN cron
RUN useradd openrepairplatform

#CMD /start.sh
