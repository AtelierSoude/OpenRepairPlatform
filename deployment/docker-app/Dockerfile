FROM python:3-stretch

# install nodejs for npm
# see http://linuxbsdos.com/2017/06/26/how-to-install-node-js-lts-on-debian-9-stretch/
RUN apt-get -y update && \
    apt-get -y install apt-utils aptitude
RUN aptitude -y upgrade && \
    aptitude -y install curl && \
    aptitude -y clean
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN aptitude -y install nodejs

ENV PYTHONUNBUFFERED 1
RUN mkdir /ateliersoude
ADD requirements.txt /ateliersoude/
# will disappear when the volume is mounted, but that's ok
RUN pip install -r /ateliersoude/requirements.txt

EXPOSE 8000
# for manual runserver and ipdb
EXPOSE 8001
CMD sh /ateliersoude/bootstrap.sh
