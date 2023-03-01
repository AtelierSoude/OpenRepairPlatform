#!/bin/bash

dropdb openrepairplatform
createdb openrepairplatform
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser
