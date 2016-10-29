# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from flask import current_app as app

import yaml

auth = HTTPBasicAuth()

def get_users():
    try:
        with open(app.config['users'], 'r') as content:
            allowed_users = yaml.load(content)
            if allowed_users is None:
                message = "Users config file empty"
                app.logger.error(message)
                return[message]
            return allowed_users
    except IOError:
        message = "Users config file not found."
        app.logger.error(message)
        return[message]

def get_roles(username):
    allowed_users = get_users()
    return allowed_users[username]["role"]

@auth.get_password
def get_password(username):
    allowed_users = get_users()
    app.logger.debug("request from {0}".format(username))
    if username in allowed_users:
        return allowed_users[username]["password"]
    return

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
