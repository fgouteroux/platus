# -*- coding: utf-8 -*-
import os
import requests
from celery import Celery
from datetime import timedelta

app = Celery()

class Config:
    REDIS_URL =  os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    BROKER_URL = REDIS_URL
    BROKER_HEARTBEAT = 10
    CELERY_RESULT_BACKEND = REDIS_URL
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
        }
    }

app.config_from_object(Config)

@app.task(name='update-services-status')
def update_service_status():
    host = os.getenv('PLATUS_HOST', 'localhost')
    port = os.getenv('PLATUS_PORT', 5001)
    username = os.getenv('PLATUS_USER', 'admin')
    password = os.getenv('PLATUS_PASS', 'admin')
    url = "http://{0}:{1}/api/v1.0/status".format(host, port)
    response = requests.get(url, auth=(username, password))
    return response.status_code
