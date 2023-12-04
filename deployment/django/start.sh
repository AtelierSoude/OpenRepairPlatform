#!/usr/bin/env bash
env > /etc/default/locale

echo "Start cron"
cron
echo "cron started"

python3 ./manage.py assets build
python3 ./manage.py migrate
python3 ./manage.py shell -c "from openrepairplatform.user.models import CustomUser; CustomUser.objects.filter(email='admin@example.com').exists() or CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true
python3 ./manage.py collectstatic --noinput --clear

npm run buildprod -prefix /srv/static/

uwsgi uwsgi.ini
