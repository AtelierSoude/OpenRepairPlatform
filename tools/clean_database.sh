#! /usr/bin/bash

set -euo pipefail

dropdb ateliersoude
createdb ateliersoude
psql ateliersoude < ../dump_28-12-2021_13_15_50.sql

./manage.py createsuperuser

./manage.py shell -c "from openrepairplatform.user.models import Organization, CustomUser; Organization.objects.first().admins.add(CustomUser.objects.get(email='lucien@hashbang.fr')); print(Organization.objects.first().admins.all())"
