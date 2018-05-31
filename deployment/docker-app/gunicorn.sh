#!/bin/sh
python /ateliersoude/manage.py collectstatic --noinput
/usr/local/bin/gunicorn ateliersoude.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/ateliersoude
