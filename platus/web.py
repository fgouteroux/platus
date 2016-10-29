# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from flask import Blueprint, render_template, request, jsonify

from platus import controllers
from platus.auth import auth, get_roles

web = Blueprint("web", __name__)
logger = logging.getLogger(__name__)


@web.route('/', methods=['GET'])
@auth.login_required
def index():
    try:
        if request.method == "GET":
            roles = get_roles(auth.username())
            return render_template('index.html', plugins=controllers.plugins_status(roles))
    except:
        raise
        return jsonify({'result': 'none'}), 401
