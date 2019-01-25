FROM python:3.6

# install nodejs for npm
# see http://linuxbsdos.com/2017/06/26/how-to-install-node-js-lts-on--9-stretch/
RUN apt-get -y update && \
    apt-get -y install apt-utils aptitude
RUN aptitude -y upgrade && \
    aptitude -y install curl && \
    aptitude -y clean
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN aptitude -y install nodejs

# French ENV for date
RUN apt-get install -y locales locales-all
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL fr_FR
ENV LANG fr_FR
ENV LANGUAGE fr_FR

ENV PYTHONUNBUFFERED 1

ADD deployment/docker-app/requirements.txt /ateliersoude/
ADD deployment/docker-app/entrypoint.sh /ateliersoude/
ADD deployment/docker-app/bootstrap.sh /ateliersoude/
# will disappear when the volume is mounted, but that's ok
RUN pip install -r /ateliersoude/requirements.txt
RUN pip install django-activity-stream
# COPY ./deployment/docker-app/bootstrap.sh /ateliersoude/bootstrap.sh
# COPY ./deployment/docker-app/entrypoint.sh /ateliersoude/entrypoint.sh
# COPY . /ateliersoude
RUN sed -i 's/\r//' /ateliersoude/entrypoint.sh
RUN sed -i 's/\r//' /ateliersoude/bootstrap.sh

#May be useless
# EXPOSE 8000
# for manual runserver and ipdb
# EXPOSE 8001
# ENTRYPOINT ["/ateliersoude/entrypoint.sh"]

#CMD bash /ateliersoude/bootstrap.sh
