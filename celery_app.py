# -*- coding: utf-8 -*-
from flask import Flask
import os
import requests
from celery import Celery
from platus.config import celery as celeryconfig

app = Celery('app')
app.config_from_object(celeryconfig)

@app.task(name='update-services-status')
def update_service_status():
    host = os.getenv('PLATUS_HOST', 'localhost')
    port = os.getenv('PLATUS_PORT', 5001)
    username = os.getenv('PLATUS_USER', 'admin')
    password = os.getenv('PLATUS_PASS', 'admin')
    url = "http://{0}:{1}/api/v1.0/status".format(host, port)
    response = requests.get(url, auth=(username, password))
    return response.status_code
