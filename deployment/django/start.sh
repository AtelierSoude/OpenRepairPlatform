#!/usr/bin/env bash
env > /etc/default/locale

echo "Start cron"
cron
echo "cron started"

npm install -prefix /srv/static/
npm run buildprod -prefix /srv/static/ &

uv run ./manage.py migrate
uv run ./manage.py shell -c "from openrepairplatform.user.models import CustomUser; CustomUser.objects.filter(email='admin@example.com').exists() or CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true

uwsgi uwsgi.ini
