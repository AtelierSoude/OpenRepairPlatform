#!/usr/bin/env bash
env > /etc/default/locale

echo "Start cron"
cron
echo "cron started"

python3 manage.py migrate
python3 manage.py shell -c "from openrepairplatform.user.models import CustomUser; CustomUser.objects.filter(email='admin@example.com').exists() or CustomUser.objects.create_superuser('admin@example.com', 'adminpass')" || true

npm install -prefix /srv/static/ 
npm run build -prefix /srv/static/ 

#python3  manage.py runserver 0.0.0.0:80 --noreload --insecure &
#python3  manage.py livereload --host=0.0.0.0


#ptvsd --host 0.0.0.0 --port 5678 &
#
#uwsgi ./uwsgi.ini
