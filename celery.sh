#!/bin/bash
cd /ateliersoude;
celery worker --app=ateliersoude.celery:app -B -l INFO --pidfile="/tmp/celerybeat.pid"
