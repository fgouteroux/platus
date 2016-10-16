# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from flask import current_app as app

auth = HTTPBasicAuth()

allowed_users = {
    "admin": {
        "password": "admin"
    }
}

@auth.get_password
def get_password(username):
    app.logger.debug("request from {0}".format(username))
    if username in allowed_users:
        return allowed_users[username]["password"]
    return

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
