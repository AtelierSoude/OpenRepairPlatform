#!/usr/bin/env bash

sed -i "s/{{SECRET_KEY}}/${SECRET_KEY}/" /etc/cron.d/openrepairplatform
sed -i "s/{{EMAIL_PASSWORD}}/${EMAIL_PASSWORD}/" /etc/cron.d/openrepairplatform
service cron start
chown -R openrepairplatform:openrepairplatform /srv/*
python3 ../../manage.py migrate
python3 ../../manage.py shell -c "from openrepairplatform.user.models import CustomUser; CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true
python3 ../../manage.py collectstatic --noinput
uwsgi ./uwsgi.ini
