#!/usr/bin/env bash

# run this in the docker container after launching the postgres instance

cd /ateliersoude/

if ! [[ -e /bootstrap_done ]]; then
    echo '\e[1;32m'"--- bootstrapping the application ---"'\e[0m'
    python3 manage.py makemigrations
    python3 manage.py migrate --noinput
    python3 manage.py shell < bootstrap.py
    python3 manage.py loaddata users/fixtures/users/*.json
    python3 manage.py loaddata plateformeweb/fixtures/*.json
    python3 manage.py shell -c 'from npm.finders import npm_install; npm_install()'
    python3 manage.py collectstatic --verbosity 1
    echo '\e[1;32m'"--- done bootstrapping ---"'\e[0m'
fi
touch /bootstrap_done

# run dev server...
if [[ "$DJANGO_DEBUG" = "1" ]]; then
    ./manage.py runserver 0.0.0.0:8001

# ...or run gunicorn server
else
    gunicorn ateliersoude.wsgi:application \
        --access-logfile - \
        --error-logfile - \
        --workers 4 \
        -b 0.0.0.0:8000 \
        --log-level ${LOGLEVEL:-INFO} \
        --worker-class gevent \
        --timeout 1200
fi
