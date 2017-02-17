import os
from datetime import timedelta

redis_url =  os.getenv('REDIS_URL', 'redis://localhost:6379/0')

BROKER_URL = redis_url
BROKER_HEARTBEAT = 10
CELERY_RESULT_BACKEND = redis_url
CELERY_TASK_RESULT_EXPIRES = 1 * 3600
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ACKS_LATE = False
CELERY_ANNOTATIONS = {'*': {'max_retries': 10, 'default_retry_delay': 60}},
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_TASK_SOFT_TIME_LIMIT = 600
CELERYD_TASK_TIME_LIMIT = 1800
CELERY_ENABLE_UTC = True
CELERY_IGNORE_RESULT = True
CELERYBEAT_SCHEDULE = {
    'update-status': {
        'task': 'update-services-status',
        'schedule': timedelta(seconds=60),
    },
}
