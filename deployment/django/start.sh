#!/usr/bin/env bash

service cron start
python3 ./manage.py migrate
python3 ./manage.py shell -c "from openrepairplatform.user.models import CustomUser; CustomUser.objects.filter(email='admin@example.com').exists() or CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true
uwsgi ./uwsgi.ini
