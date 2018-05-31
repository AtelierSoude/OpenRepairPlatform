# List of modules to import when celery starts.
CELERY_IMPORTS = ('tasks', )

# Broker settings.
BROKER_TRANSPORT = 'redis'
BROKER_HOST = 'redis:///localhost'
BROKER_PORT = 5672
BROKER_VHOST = '/'
BROKER_USER = 'guest'
BROKER_PASSWORD = 'guest'

## Worker settings
CELERYD_CONCURRENCY = 1
CELERYD_TASK_TIME_LIMIT = 20
# CELERYD_LOG_FILE = 'celeryd.log'
CELERYD_LOG_LEVEL = 'INFO'
