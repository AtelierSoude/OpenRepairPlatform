from celery import Celery
from celery import task
import os

celery = Celery('ateliersoude', broker='redis://password@redis:6379/0') #!
os.environ[ 'DJANGO_SETTINGS_MODULE' ] = "settings"

@task()
def add_photos_task( lad_id ):
    print("HelLO WORkLD")
