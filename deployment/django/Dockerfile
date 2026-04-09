################ BASE #########################
FROM python:3.13-slim-bullseye AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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

RUN apt-get install -y libproj-dev locales locales-all cron gdal-bin build-essential sassc libcups2-dev
RUN apt-get install --assume-yes git

RUN ln /usr/bin/sassc /usr/bin/sass

# Install UV globally
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    cp /root/.local/bin/uvx /usr/local/bin/uvx

# French ENV for date
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LC_ALL=fr_FR
ENV LANG=fr_FR
ENV LANGUAGE=fr_FR

RUN mkdir -p /srv/app /srv/static /srv/media

RUN groupadd -r openrepairplatform
RUN useradd -ms /bin/bash -r -g openrepairplatform openrepairplatform
RUN usermod -G openrepairplatform,www-data openrepairplatform
RUN chown -R openrepairplatform:openrepairplatform /srv/*

RUN mkdir /var/uwsgi
RUN touch /var/uwsgi/openrepairplatform.sock
RUN chown openrepairplatform:www-data /var/uwsgi
RUN chown openrepairplatform:www-data /var/uwsgi/openrepairplatform.sock
RUN chmod 660 /var/uwsgi/openrepairplatform.sock

WORKDIR /srv/app

COPY ../../pyproject.toml ./
RUN uv sync

ENV PATH="/srv/app/.venv/bin:/usr/local/bin:$PATH"

RUN echo "alias rsp='uv run manage.py runserver 0.0.0.0:8005'" >> /root/.bashrc

COPY deployment/django/openrepairplatform.cron /etc/cron.d/openrepairplatform
RUN chmod 0644 /etc/cron.d/openrepairplatform
RUN chown openrepairplatform:openrepairplatform /etc/default/locale
RUN crontab /etc/cron.d/openrepairplatform
RUN chmod u+s /usr/sbin/cron

COPY manage.py .

################ BUILDER #########################
FROM base AS builder

WORKDIR /srv/app

################ DEVEVOPPEMENT #########################

FROM base AS developpement

WORKDIR /srv/app/

RUN uv pip install ptvsd

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
RUN uv run ./manage.py collectstatic --noinput --clear

COPY ../../openrepairplatform/static /srv/static
RUN uv run ./manage.py assets build

COPY deployment/django/start.sh .
COPY deployment/django/uwsgi.ini .

RUN chown -R openrepairplatform:openrepairplatform /srv/*

USER openrepairplatform
EXPOSE 8000

ENTRYPOINT ["./start.sh"]