#!/usr/bin/env python3
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
import logging

# don't choke if
try:
    User.objects.create_superuser('admin','admin@example.com','foobar')
except IntegrityError:
    logging.info("admin user was already created, moving on")
    pass


