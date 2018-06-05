#!/bin/bash
set -e
export REDIS_URL=redis://redis:6379

# the official postgres image uses 'postgres' as default user if not set explictly.
if [ -z "$POSTGRES_USER" ]; then
    export POSTGRES_USER=postgres
fi

export DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@ateliersoude-postgres:5432/$POSTGRES_USER
export CELERY_BROKER_URL=$REDIS_URL/0
exec "$@"
