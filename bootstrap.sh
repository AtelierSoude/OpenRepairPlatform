#!/usr/bin/env bash

# run this in the docker container after launching the postgres instance

cd /ateliersoude/

if ! [ -e /bootstrap_done ]; then
    echo "--- bootstrapping the application ---"
    python3 manage.py makemigrations || exit 1
    python3 manage.py migrate --noinput || exit 1
    python3 manage.py shell < bootstrap.py
    #python3 manage.py loaddata quotation/fixtures/quotation/*.json
    python3 manage.py collectstatic
    echo "--- done bootstrapping ---"
fi
touch /bootstrap_done
# TODO remove --insecure and handle static files properly
# https://docs.djangoproject.com/fr/1.11/ref/contrib/staticfiles/
#python3 manage.py runserver --insecure 0.0.0.0:8000

gunicorn ateliersoude.wsgi:application \
    --access-logfile - \
    --error-logfile - \
    --workers 4 \
    -b 0.0.0.0:8000 \
    --log-level DEBUG \
    --worker-class gevent \
    --timeout 1200
