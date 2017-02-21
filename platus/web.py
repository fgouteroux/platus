# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from flask import Blueprint, render_template, request, jsonify

from platus import controllers
from platus.auth import auth, get_roles

# Import third party libs
from flask import current_app as app

web = Blueprint("web", __name__)
logger = logging.getLogger(__name__)


@web.route('/', methods=['GET'])
@auth.login_required
def index():
    try:
        if request.method == "GET":
            current_user = auth.username()
            roles = get_roles(current_user)

            return render_template(
                'index.html',
                config=app.config,
                current_user=current_user,
                services=controllers.services_status(roles))
    except:
        raise
        return jsonify({'result': 'none'}), 401
