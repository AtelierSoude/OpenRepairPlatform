#!/usr/bin/env python3
from django.db.utils import IntegrityError
from users.models import CustomUser
import logging

# don't choke if
try:
    CustomUser.objects.create_superuser('admin@example.com','foobar')
except IntegrityError:
    logging.info("admin user was already created, moving on")
    pass


