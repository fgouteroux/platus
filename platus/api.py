# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

import requests
from flask import Blueprint, render_template, request, jsonify

from platus import controllers
from platus.auth import auth, get_roles

api = Blueprint("api", __name__, url_prefix='/api/v1.0')

@api.route('/health', methods=['GET'])
def health():
    data = {
        "health": "Good doctor!"
    }
    return jsonify(data), 200


@api.route('/status', methods=['GET'])
@auth.login_required
def status():
    try:
        if request.method == "GET":
            roles = get_roles(auth.username())
            return jsonify({'result': controllers.plugins_status(roles)}), 200
    except:
        raise
        return jsonify({'result': 'none'}), 401
