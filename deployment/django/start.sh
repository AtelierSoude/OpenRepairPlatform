#!/usr/bin/env bash

sed -i "s/{{SECRET_KEY}}/${SECRET_KEY}/" /etc/cron.d/openrepairplatform
sed -i "s/{{EMAIL_PASSWORD}}/${EMAIL_PASSWORD}/" /etc/cron.d/openrepairplatform

service cron start

python3 ./manage.py migrate
python3 ./manage.py shell -c "from openrepairplatform.user.models import CustomUser; CustomUser.objects.filter(email='admin@example.com').exists() or CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true
#python3 ./manage.py collectstatic --noinput

npm run buildprod -prefix ../../openrepairplatform/static/
 

uwsgi uwsgi.ini
