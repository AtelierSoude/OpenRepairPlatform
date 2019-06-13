#!/usr/bin/env bash

rm /start.sh
sed -i "s/{{SECRET_KEY}}/${SECRET_KEY}/" /etc/cron.d/ateliersoude
sed -i "s/{{EMAIL_PASSWORD}}/${EMAIL_PASSWORD}/" /etc/cron.d/ateliersoude
service cron start
chown -R ateliersoude:ateliersoude /srv/*
python3 manage.py migrate
python3 manage.py shell -c "from ateliersoude.user.models import CustomUser; CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true
python3 manage.py collectstatic --noinput
uwsgi uwsgi.ini
