#!/usr/bin/env bash

## for cron
printenv > /etc/default/locale

python3 manage.py migrate
python3 manage.py shell -c "from openrepairplatform.user.models import CustomUser; CustomUser.objects.filter(email='admin@example.com').exists() or CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true
#python3 ../../manage.py collectstatic --noinput
#uwsgi ./uwsgi.ini
npm run build -prefix /srv/app/openrepairplatform/static/ &
#python3 ../../manage.py runserver 0.0.0.0:80 --insecure &
service cron start
#python3 -m ptvsd --host 0.0.0.0 --port 5678 ../../manage.py runserver 0.0.0.0:80 --noreload --insecure &
python3  manage.py runserver 0.0.0.0:80 --noreload --insecure &
python3  manage.py livereload --host=0.0.0.0


#ptvsd --host 0.0.0.0 --port 5678 &
#
#uwsgi ./uwsgi.ini
