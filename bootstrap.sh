#!/usr/bin/env bash

# run this in the docker container after launching the postgres instance

cd /ateliersoude/

if ! [ -e /bootstrap_done ]; then
    echo "--- bootstrapping the application ---"
    python3 manage.py makemigrations || exit 1
    python3 manage.py migrate --noinput || exit 1
    python3 manage.py shell < bootstrap.py
    #python3 manage.py loaddata quotation/fixtures/quotation/*.json
    python3 manage.py collectstatic --verbosity 0
    echo "--- done bootstrapping ---"
fi
touch /bootstrap_done
# TODO remove --insecure and handle static files properly
# https://docs.djangoproject.com/fr/1.11/ref/contrib/staticfiles/
#python3 manage.py runserver --insecure 0.0.0.0:8000

# todo: make this smarter (env var in the docker container, passed by
# rebuild-and-start.sh, add another one)
if [ "$DJANGO_DEBUG" = "1" ]
    then GUNICORN_LOGLEVEL="DEBUG"
else
    GUNICORN_LOGLEVEL="INFO"
fi

gunicorn ateliersoude.wsgi:application \
    --access-logfile - \
    --error-logfile - \
    --workers 4 \
    -b 0.0.0.0:8000 \
    --log-level $GUNICORN_LOGLEVEL \
    --worker-class gevent \
    --timeout 1200
