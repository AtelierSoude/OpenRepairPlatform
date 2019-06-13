#!/bin/bash

dropdb ateliersoude
createdb ateliersoude
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser
